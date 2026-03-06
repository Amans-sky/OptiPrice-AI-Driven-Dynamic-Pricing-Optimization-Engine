"""Generate synthetic market data for testing and demonstration."""

import os
import csv
import numpy as np
import logging
from datetime import datetime, timedelta
from config import PATHS, ENVIRONMENT_CONFIG

logger = logging.getLogger(__name__)


class MarketSimulator:
    """Simulate market dynamics for training/testing data generation."""
    
    def __init__(self, 
                 base_demand=1000.0,
                 elasticity=-1.5,
                 competitor_price_init=25.0,
                 volatility=0.05):
        """Initialize market simulator.
        
        Args:
            base_demand: Base demand level
            elasticity: Price elasticity of demand
            competitor_price_init: Initial competitor price
            volatility: Price volatility (std dev of random walk)
        """
        self.base_demand = base_demand
        self.elasticity = elasticity
        self.competitor_price = competitor_price_init
        self.volatility = volatility
        self.demand_level = base_demand
        self.prices = []
        self.demands = []
        self.competitor_prices = []
        
    def step(self, my_price):
        """Simulate one market step.
        
        Args:
            my_price: My current price
            
        Returns:
            Tuple of (demand, competitor_price, revenue)
        """
        # Update competitor price with random walk
        drift = np.random.normal(0, self.volatility)
        self.competitor_price = max(5, self.competitor_price + drift)
        
        # Update demand level with slight trend
        demand_drift = np.random.normal(0, 50)
        self.demand_level = np.clip(self.demand_level + demand_drift, 0, 200)
        
        # Calculate demand using price elasticity
        relative_price = my_price / max(self.competitor_price, 1.0)
        demand = self.base_demand * np.power(relative_price, self.elasticity)
        demand = max(0, demand)
        
        revenue = my_price * demand
        
        # Store history
        self.prices.append(my_price)
        self.demands.append(demand)
        self.competitor_prices.append(self.competitor_price)
        
        return demand, self.competitor_price, revenue
    
    def reset(self):
        """Reset simulator."""
        self.prices = []
        self.demands = []
        self.competitor_prices = []
        self.competitor_price = ENVIRONMENT_CONFIG['competitor_price_init']
        self.demand_level = self.base_demand


def generate_market_data(
    num_periods=365, 
    output_file=None,
    price_points=None):
    """Generate synthetic market data with different pricing strategies.
    
    Args:
        num_periods: Number of time periods to simulate
        output_file: Path to save CSV. If None, uses default data path
        price_points: List of price points to test. If None, uses 10-50 in steps of 5
        
    Returns:
        List of market data records
    """
    if output_file is None:
        os.makedirs(PATHS['data_dir'], exist_ok=True)
        output_file = os.path.join(PATHS['data_dir'], 'sample_market_data.csv')
    
    if price_points is None:
        price_points = np.arange(
            ENVIRONMENT_CONFIG['price_min'],
            ENVIRONMENT_CONFIG['price_max'] + 1,
            ENVIRONMENT_CONFIG['price_step']
        )
    
    logger.info(f"Generating synthetic market data ({num_periods} periods)...")
    
    simulator = MarketSimulator(
        base_demand=ENVIRONMENT_CONFIG['base_demand'],
        elasticity=ENVIRONMENT_CONFIG['elasticity']
    )
    
    records = []
    start_date = datetime.now()
    
    for period in range(num_periods):
        # Cycle through different prices for each period
        price = price_points[period % len(price_points)]
        
        demand, competitor_price, revenue = simulator.step(price)
        
        date = start_date + timedelta(days=period)
        
        record = {
            'date': date.strftime('%Y-%m-%d'),
            'period': period,
            'my_price': round(price, 2),
            'competitor_price': round(competitor_price, 2),
            'demand': round(demand, 2),
            'revenue': round(revenue, 2),
            'inventory_change': round(np.random.normal(0, 100), 2)
        }
        
        records.append(record)
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if records:
        keys = records[0].keys()
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)
        
        logger.info(f"✓ Market data saved: {output_file}")
        logger.info(f"  Records: {len(records)}")
        logger.info(f"  Avg Revenue: ${np.mean([r['revenue'] for r in records]):.2f}")
        logger.info(f"  Avg Demand: {np.mean([r['demand'] for r in records]):.1f} units")
    
    return records


def generate_agent_dataset(model, num_episodes=50, output_file=None):
    """Generate dataset by running trained agent.
    
    Args:
        model: Trained DQN model
        num_episodes: Number of episodes to simulate
        output_file: Path to save CSV
        
    Returns:
        List of episodes data
    """
    import torch
    from src.environment import PricingEnvironment
    
    if output_file is None:
        os.makedirs(PATHS['data_dir'], exist_ok=True)
        output_file = os.path.join(PATHS['data_dir'], 'agent_episodes.csv')
    
    logger.info(f"Generating agent dataset ({num_episodes} episodes)...")
    
    env = PricingEnvironment(max_steps=ENVIRONMENT_CONFIG['max_steps_per_episode'])
    records = []
    
    for episode in range(num_episodes):
        state = env.reset()
        done = False
        episode_reward = 0.0
        step = 0
        
        while not done and step < ENVIRONMENT_CONFIG['max_steps_per_episode']:
            state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            
            with torch.no_grad():
                q_values = model(state_t)
                action = torch.argmax(q_values).item()
            
            next_state, reward, done, info = env.step(action)
            episode_reward += reward
            
            # Get current price from action
            price = env.price_levels[action]
            
            record = {
                'episode': episode,
                'step': step,
                'demand_level': round(state[0], 2),
                'competitor_price': round(state[1], 2),
                'inventory_level': round(state[2], 2),
                'action': action,
                'price': round(float(price), 2),
                'reward': round(reward, 2),
                'q_max': round(float(torch.max(q_values).item()), 2)
            }
            
            records.append(record)
            state = next_state
            step += 1
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if records:
        keys = records[0].keys()
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)
        
        logger.info(f"✓ Agent dataset saved: {output_file}")
        logger.info(f"  Records: {len(records)}")
        logger.info(f"  Episodes: {num_episodes}")
    
    return records


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Generate market data
    market_data = generate_market_data(num_periods=365)
    
    print(f"\n✓ Generated {len(market_data)} market data records")
    print(f"  Sample: {market_data[0]}")
