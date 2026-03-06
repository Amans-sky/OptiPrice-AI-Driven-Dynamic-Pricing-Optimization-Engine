"""FastAPI endpoint for DQN-based price recommendations."""

from fastapi import FastAPI, HTTPException
import os
import sys
import logging
import torch
import numpy as np
import glob

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import API_CONFIG, PATHS, ENVIRONMENT_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dynamic Pricing Recommendation API",
    description="AI-driven pricing optimization service using Deep Q-Networks (DQN)",
    version="1.0"
)

# Price levels
price_levels = np.arange(
    ENVIRONMENT_CONFIG['price_min'],
    ENVIRONMENT_CONFIG['price_max'] + 1,
    ENVIRONMENT_CONFIG['price_step']
)

logger.info(f"Available price levels: {price_levels}")


def find_latest_model():
    """Find the most recent model file."""
    model_files = glob.glob(os.path.join(PATHS['model_dir'], 'dqn_pricing_model_*.pth'))
    if not model_files:
        return None
    return max(model_files, key=os.path.getctime)


def load_model(model_path=None):
    """Load trained DQN model.
    
    Args:
        model_path: Path to model file. If None, finds latest.
        
    Returns:
        Loaded model or None
    """
    if model_path is None:
        model_path = find_latest_model()
    
    if not model_path or not os.path.exists(model_path):
        logger.warning("No trained model found")
        return None
    
    try:
        from src.dqn_agent import DQN
        state_size = 3
        action_size = len(price_levels)
        model = DQN(state_size, action_size)
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        model.eval()
        logger.info(f"Model loaded successfully: {model_path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return None


# Load model at startup
MODEL = load_model()


@app.get('/recommend_price')
def recommend_price(
    demand_level: float = API_CONFIG['default_demand_level'],
    competitor_price: float = API_CONFIG['default_competitor_price'],
    inventory_level: float = API_CONFIG['default_inventory_level']
):
    """Get AI-recommended price for given market conditions.

    Args:
        demand_level: Current market demand (0-200)
        competitor_price: Competitor's current price ($)
        inventory_level: Current inventory units

    Returns:
        JSON with recommended price, source, and state info
    """
    logger.info(
        f"Price recommendation request: demand={demand_level:.1f}, "
        f"competitor_price=${competitor_price:.2f}, inventory={inventory_level:.0f}"
    )
    
    # Fallback analytic recommendation
    if MODEL is None:
        elasticity = ENVIRONMENT_CONFIG['elasticity']
        base_demand = ENVIRONMENT_CONFIG['base_demand']
        
        # Calculate demand for each price point
        demands = base_demand * np.power(price_levels / max(competitor_price, 1.0), elasticity)
        revenues = price_levels * demands
        best_idx = np.argmax(revenues)
        best_price = float(price_levels[best_idx])
        
        logger.info(f"Using analytic fallback: ${best_price:.2f}")
        
        return {
            "recommended_price": best_price,
            "source": "analytic_fallback",
            "reason": "Trained model not available",
            "expected_demand": float(demands[best_idx]),
            "expected_revenue": float(revenues[best_idx])
        }
    
    # Use DQN model
    try:
        state = torch.tensor(
            [[demand_level, competitor_price, inventory_level]],
            dtype=torch.float32
        )
        
        with torch.no_grad():
            q_values = MODEL(state)
            action = int(torch.argmax(q_values).item())
            recommended_price = float(price_levels[action])
        
        logger.info(f"DQN recommendation: ${recommended_price:.2f}")
        
        return {
            "recommended_price": recommended_price,
            "source": "dqn_model",
            "state": {
                "demand_level": demand_level,
                "competitor_price": competitor_price,
                "inventory_level": inventory_level
            },
            "q_values": {
                str(price): float(q.item()) 
                for price, q in zip(price_levels, q_values[0])
            }
        }
    
    except Exception as e:
        logger.error(f"Model inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.get('/health')
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if MODEL is not None else "degraded",
        "model_loaded": MODEL is not None,
        "version": "1.0"
    }


@app.get('/config')
def get_config():
    """Return current configuration."""
    return {
        "environment": ENVIRONMENT_CONFIG,
        "api": API_CONFIG,
        "price_range": {
            "min": float(ENVIRONMENT_CONFIG['price_min']),
            "max": float(ENVIRONMENT_CONFIG['price_max']),
            "step": float(ENVIRONMENT_CONFIG['price_step'])
        }
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
