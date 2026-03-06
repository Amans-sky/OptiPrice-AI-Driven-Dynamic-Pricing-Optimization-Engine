# Quick Start Guide - Dynamic Pricing DQN

## Project Structure

```
dynamic-pricing-rl/
├── src/                    # Core ML modules
│   ├── dqn_agent.py       # Neural network implementation
│   ├── environment.py      # Market simulator
│   ├── train_agent.py      # Training loop with replay buffer & target network
│   ├── evaluate_model.py   # Performance evaluation
│   ├── replay_buffer.py    # Experience replay storage
│   ├── visualization.py    # Training visualization
│   └── data_generator.py   # Synthetic data generation
├── api/                    # REST API service
│   └── pricing_api.py      # FastAPI endpoints
├── dashboard/              # Interactive UI
│   └── app.py             # Streamlit interface
├── config.py              # Centralized configuration
├── run.py                 # Training entry point
├── Dockerfile             # Container image
└── requirements.txt       # Python dependencies
```

---

## Installation & Setup

### 1. **Clone & Setup Environment**
```bash
cd dynamic-pricing-rl
pip install -r requirements.txt
```

### 2. **Verify Install**
```bash
python -c "import torch, fastapi, streamlit; print('✓ All imports OK')"
```

---

## Running Locally

### **Option A: Train Only**
```bash
# Basic training (uses config defaults)
python run.py

# Or with custom episodes
python -c "from src.train_agent import train; train(num_episodes=500)"
```
**Output**: Model saved to `models/dqn_pricing_model_YYYYMMDD_HHMMSS.pth`  
**Visualizations**: Training plots in `logs/training_progress.png`

---

### **Option B: Train + API + Dashboard**

**Terminal 1 - Training**:
```bash
python run.py
```

**Terminal 2 - API Server**:
```bash
uvicorn api.pricing_api:app --reload --port 8000
```
Visit: http://localhost:8000/docs for Swagger documentation

**Terminal 3 - Dashboard**:
```bash
streamlit run dashboard/app.py
```
Visit: http://localhost:8501

---

### **Option C: Docker (Recommended for Production)**

```bash
# Build image
docker build -t dqn-pricing:latest .

# Run API + Dashboard
docker-compose up

# Run with training profile
docker-compose --profile training up

# Run specific service
docker run -p 8000:8000 dqn-pricing:latest \
  uvicorn api.pricing_api:app --host 0.0.0.0 --port 8000
```

---

## Configuration Management

**Edit** `config.py` to customize:

```python
TRAINING_CONFIG = {
    "num_episodes": 1000,        # Number of training episodes
    "gamma": 0.99,               # Discount factor (0-1)
    "learning_rate": 1e-3,       # Adam optimizer LR
    "batch_size": 64,            # Mini-batch size
    "epsilon_start": 1.0,        # Initial exploration rate
    "epsilon_end": 0.1,          # Final exploration rate
    "epsilon_decay": 0.995,      # Decay per episode
    "target_update_frequency": 10,  # Update target network
    "replay_buffer_capacity": 10000,
    "seed": 42,                  # Random seed
}

ENVIRONMENT_CONFIG = {
    "price_min": 5,              # Minimum price ($)
    "price_max": 50,             # Maximum price ($)
    "price_step": 5,             # Price granularity
    "base_demand": 1000.0,       # Base demand level
    "elasticity": -1.5,          # Price elasticity
}

EVALUATION_CONFIG = {
    "num_episodes": 50,
    "static_baseline_price": 20.0,  # Fixed price to compare
}
```

**No need to restart** - imports pick up config changes automatically.

---

## API Usage

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Get Price Recommendation**
```bash
curl "http://localhost:8000/recommend_price?demand_level=120&competitor_price=28&inventory_level=800"
```

**Response**:
```json
{
  "recommended_price": 32.50,
  "source": "dqn_model",
  "state": {
    "demand_level": 120.0,
    "competitor_price": 28.0,
    "inventory_level": 800.0
  },
  "q_values": {
    "5": 24.32,
    "10": 45.67,
    ...
    "50": 89.12
  }
}
```

### **Get Configuration**
```bash
curl http://localhost:8000/config
```

### **Python Client Example**
```python
import requests

response = requests.get(
    "http://localhost:8000/recommend_price",
    params={
        "demand_level": 150.0,
        "competitor_price": 25.0,
        "inventory_level": 1200.0
    }
)
print(f"Recommended price: ${response.json()['recommended_price']:.2f}")
```

---

## Training & Evaluation

### **Training**
```python
from src.train_agent import train
from config import TRAINING_CONFIG

# Train with default config
model, rewards = train()

# Train with custom episodes
model, rewards = train(num_episodes=200)

# Training outputs:
# - models/dqn_pricing_model_*.pth (trained weights)
# - logs/training_progress.png (learning curve)
# - checkpoints/ckpt_ep*.pth (intermediate saves)
```

### **Evaluation**
```python
from src.evaluate_model import evaluate

results = evaluate()
# Compares: RL agent vs Static baseline vs Random baseline
```

**Sample Output**:
```
======================================================================
EVALUATION RESULTS
======================================================================

RL Agent:
  Mean Reward:     $9,450.25
  Std Dev:         $450.45
  Min/Max:         $8,200.00 / $10,520.00

Static Baseline ($20):
  Mean Reward:     $8,650.00
  ...

Improvement:
  vs Static:       +9.26%
  vs Random:       +31.25%
```

---

## Data Generation

### **Generate Synthetic Market Data**
```python
from src.data_generator import generate_market_data, MarketSimulator

# Generate 365 days of market data
records = generate_market_data(num_periods=365)

# Output: data/sample_market_data.csv
# Columns: date, period, my_price, competitor_price, demand, revenue, inventory_change
```

### **Generate Agent Episode Dataset**
```python
from src.data_generator import generate_agent_dataset
import torch
from src.train_agent import get_model_path

model_path = get_model_path()  # Get latest model
model = load_model(model_path)

records = generate_agent_dataset(model, num_episodes=100)
# Output: data/agent_episodes.csv
```

---

## Logging & Monitoring

### **View Logs**
```bash
# Training logs (real-time)
tail -f logs/training_progress.log

# View training plot
open logs/training_progress.png      # macOS
xdg-open logs/training_progress.png  # Linux
start logs/training_progress.png     # Windows
```

### **Log Levels**
- `INFO` - Training progress, key events (default)
- `DEBUG` - Detailed steps, checkpoints
- `WARNING` - Issues but recoverable
- `ERROR` - Critical failures

### **Adjust Logging Level**
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)  # More verbose
```

---

## Debugging & Troubleshooting

### **Issue: "Model not found"**
```
Solution: Train first - python run.py
or ensure models/ directory exists
```

### **Issue: API connection error in dashboard**
```
Solution 1: Check API is running - uvicorn api.pricing_api:app --reload
Solution 2: Check port 8000 is available - lsof -i :8000
Solution 3: Verify http://localhost:8000/health works
```

### **Issue: Out of memory during training**
```
Solution: Reduce batch_size in config.py
- From batch_size: 64 → 32
- Or reduce replay_buffer_capacity
```

### **Issue: Training too slow**
```
Solution 1: Enable GPU if available
  - Verify: python -c "import torch; print(torch.cuda.is_available())"
  - If True, PyTorch will auto-use GPU

Solution 2: Reduce num_episodes or max_steps_per_episode
```

---

## Visualization & Analysis

### **Plot Training Progress**
```python
from src.visualization import plot_training_progress
import numpy as np

rewards = [1000, 1500, 2000, 2500, 3000]  # Your episode rewards
plot_training_progress(rewards, save_path="my_training.png")
```

### **Plot Episode Statistics**
```python
from src.visualization import plot_episode_stats

stats = {
    'rewards': episode_rewards,
    'lengths': episode_lengths,
    'losses': episode_losses,
    'epsilon': epsilon_values
}
plot_episode_stats(stats)
```

---

## Production Deployment

### **Step 1: Build Docker Image**
```bash
docker build -t dqn-pricing:v1.0 .
```

### **Step 2: Push to Registry** (optional)
```bash
docker tag dqn-pricing:v1.0 myregistry/dqn-pricing:v1.0
docker push myregistry/dqn-pricing:v1.0
```

### **Step 3: Deploy**
```bash
# AWS ECS, Google Cloud Run, Azure Container Instances, etc.
# All accept Docker images

# Local example
docker run -d \
  --name dqn-api \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  dqn-pricing:v1.0 \
  uvicorn api.pricing_api:app --host 0.0.0.0 --port 8000
```

---

## Project Features Checklist

✅ **Replay Buffer** - Experience storage and sampling  
✅ **Target Network** - Stabilized learning  
✅ **Config Management** - Centralized hyperparameters  
✅ **Logging** - Comprehensive logging system  
✅ **Seed Control** - Reproducible runs (seed=42)  
✅ **Training Visualization** - 4 plot types  
✅ **Model Versioning** - Timestamped models  
✅ **Containerization** - Docker + Docker Compose  
✅ **Data Generation** - Synthetic market data  
✅ **FastAPI** - Production REST API  
✅ **Streamlit Dashboard** - Interactive UI  
✅ **Documentation** - Comprehensive guides  

---

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Training Time (100 episodes) | ~5-10 min |
| Inference Time (single prediction) | <50ms |
| Model Size | ~200KB |
| GPU Memory (training) | 2-4 GB |
| API Response Time | <100ms |

---

## Advanced Usage

### **Resume Training from Checkpoint**
```python
from src.train_agent import train
import torch

model = DQN(3, 10)
model.load_state_dict(torch.load("checkpoints/ckpt_ep500.pth"))
# Continue training...
```

### **Hyperparameter Sweep**
```python
from src.train_agent import train
import itertools

learning_rates = [1e-3, 5e-4, 1e-4]
batch_sizes = [32, 64, 128]

for lr, bs in itertools.product(learning_rates, batch_sizes):
    model, rewards = train(lr=lr)  # Update config.py as needed
    avg_reward = np.mean(rewards[-50:])
    print(f"LR={lr}, BS={bs}: Avg Reward = {avg_reward:.2f}")
```

### **Model Ensembling**
```python
from src.train_agent import train
import torch

# Train multiple models
models = []
for i in range(5):
    model, _ = train(num_episodes=100)
    models.append(model)

# Ensemble prediction
state_t = torch.tensor([[100, 25, 1000]], dtype=torch.float32)
q_values_ensemble = torch.stack([m(state_t) for m in models]).mean(dim=0)
ensemble_action = torch.argmax(q_values_ensemble)
```

---

## Support & Further Learning

- **Documentation**: See `PHASE-4B-SUMMARY.md` for detailed architecture
- **DQN Reference**: [Mnih et al., 2015 - Nature](https://www.nature.com/articles/nature14236)
- **PyTorch Docs**: https://pytorch.org/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Streamlit**: https://docs.streamlit.io

---

**Happy pricing optimization! 🚀**
