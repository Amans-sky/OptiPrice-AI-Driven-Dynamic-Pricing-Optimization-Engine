# Complete Setup Guide: Local Development + Colab Training

This guide covers running the Dynamic Pricing DQN project **locally (API + Dashboard) with training on Google Colab**.

---

## Part 1: Local Machine Setup (5 minutes)

### Step 1.1 - Clone the Repository

```bash
# Choose a folder
cd C:\Users\YourUsername\Desktop
# Or any location you prefer

# Clone the repository
git clone <your-repo-url> dynamic-pricing-rl
cd dynamic-pricing-rl
```

### Step 1.2 - Create Python Virtual Environment

```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

**Verify activation** (should show `.venv` in prompt):
```bash
# You should see (.venv) at the start of your terminal line
```

### Step 1.3 - Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Verify installation**:
```bash
python -c "import torch, fastapi, streamlit; print('✓ All imports OK')"
```

### Step 1.4 - Verify Project Structure

```bash
# List main folders
ls -la
# You should see: api/, src/, dashboard/, config.py, run.py, etc.

# Check models folder exists
mkdir -p models logs checkpoints data
```

---

## Part 2: Start API & Dashboard Locally (2 services)

### Step 2.1 - Open Terminal 1 (API Server)

```bash
# Make sure .venv is activated
.venv\Scripts\Activate.ps1

# Start FastAPI
uvicorn api.pricing_api:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test the API** (new PowerShell window):
```bash
curl http://127.0.0.1:8000/health
# Should return: {"status":"degraded","model_loaded":false,"version":"1.0"}
# (degraded because no model trained yet - this is OK!)
```

**Access Swagger docs**:
- Open browser: http://localhost:8000/docs
- Try `/health` endpoint

---

### Step 2.2 - Open Terminal 2 (Streamlit Dashboard)

```bash
# In NEW PowerShell terminal
cd C:\Users\YourUsername\Desktop\dynamic-pricing-rl
.venv\Scripts\Activate.ps1

# Start Streamlit
streamlit run dashboard/app.py
```

**Expected output**:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Open browser**: http://localhost:8501

---

## Part 3: Google Colab Training Setup (10 minutes)

### Step 3.1 - Create Colab Notebook

1. Go to https://colab.research.google.com/
2. Click `File → New notebook`
3. Rename it: "DQN Training"

### Step 3.2 - Clone Repository in Colab

**Cell 1** - Clone the repo:
```python
!git clone <your-repo-url> /content/dynamic-pricing-rl
%cd /content/dynamic-pricing-rl
!ls -la
```

**Expected**: See folders like `src/`, `api/`, `dashboard/`, `config.py`

### Step 3.3 - Install Dependencies in Colab

**Cell 2** - Install packages:
```python
!pip install -q torch torch-vision torchaudio --index-url https://download.pytorch.org/whl/cu118
!pip install -q fastapi uvicorn streamlit numpy pandas matplotlib scikit-learn requests
```

**Verify**:
```python
import torch
import numpy as np
from src.train_agent import train

print(f"✓ PyTorch version: {torch.__version__}")
print(f"✓ GPU available: {torch.cuda.is_available()}")
print(f"✓ Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
```

---

## Part 4: Train Model on Colab (varies by config)

### Step 4.1 - Quick Training (Test, ~5 min)

**Cell 3** - Short training run:
```python
from src.train_agent import train
import matplotlib.pyplot as plt

# Quick test with 100 episodes
model, rewards = train(num_episodes=100)

print(f"✓ Training complete!")
print(f"  Final reward: {rewards[-1]:.2f}")
print(f"  Best reward: {max(rewards):.2f}")
print(f"  Avg (last 10): {np.mean(rewards[-10:]):.2f}")

# Plot results
plt.figure(figsize=(12, 5))
plt.plot(rewards, alpha=0.3, label='Episode Reward')
if len(rewards) >= 10:
    ma10 = np.convolve(rewards, np.ones(10)/10, mode='valid')
    plt.plot(range(9, len(rewards)), ma10, linewidth=2, label='MA(10)')
plt.xlabel('Episode')
plt.ylabel('Total Reward ($)')
plt.title('Training Progress')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### Step 4.2 - Full Training (Best, ~30 min)

**Cell 4** - Production training:
```python
from src.train_agent import train

# Full training with 1000 episodes
model, rewards = train(num_episodes=1000)

# Summary
print("\n" + "="*60)
print("TRAINING COMPLETE")
print("="*60)
print(f"Final reward:        ${rewards[-1]:,.2f}")
print(f"Best reward:         ${max(rewards):,.2f}")
print(f"Avg (last 50):       ${np.mean(rewards[-50:]):,.2f}")
print(f"Total episodes:      {len(rewards)}")
print(f"Model saved:         models/dqn_pricing_model_*.pth")
print("="*60)
```

---

## Part 5: Download Trained Model from Colab

### Step 5.1 - List Available Models

**Cell 5**:
```python
import os
from pathlib import Path

model_dir = Path('/content/dynamic-pricing-rl/models')
model_files = list(model_dir.glob('*.pth'))

print("Available models:")
for model in sorted(model_files, key=lambda x: x.stat().st_mtime, reverse=True):
    size_mb = model.stat().st_size / (1024*1024)
    print(f"  • {model.name} ({size_mb:.1f} MB)")
```

### Step 5.2 - Download the Model

**Method A - Using Colab file browser** (easiest):
```python
from google.colab import files

# Download the latest model
model_path = sorted(model_dir.glob('*.pth'), 
                   key=lambda x: x.stat().st_mtime, 
                   reverse=True)[0]

files.download(str(model_path))
print(f"✓ Downloaded: {model_path.name}")
```

A dialog will appear. Click to download the `.pth` file.

**Method B - Using zip** (if multiple files):
```python
import shutil

# Create zip of everything
shutil.make_archive('/tmp/dqn-models', 'zip', '/content/dynamic-pricing-rl/models')
files.download('/tmp/dqn-models.zip')
```

---

## Part 6: Use Trained Model Locally

### Step 6.1 - Place Model in Local Folder

1. Your download: `dqn_pricing_model_20260304_153045.pth`
2. Move to: `C:\Users\YourUsername\Desktop\dynamic-pricing-rl\models\`

**Verify**:
```bash
ls models/
# Should show: dqn_pricing_model_*.pth
```

### Step 6.2 - Restart API (Loads New Model)

**In Terminal 1** (where API is running):
```bash
# Press Ctrl+C to stop
# Then restart
uvicorn api.pricing_api:app --reload
```

**Wait for**: `Application startup complete`

**Verify model loaded**:
```bash
curl http://127.0.0.1:8000/health
# Should return: {"status":"healthy","model_loaded":true,"version":"1.0"}
```

### Step 6.3 - Test in Dashboard

1. Go to http://localhost:8501 (Streamlit)
2. Adjust sliders:
   - Demand Level: 100-150
   - Competitor Price: $20-30
   - Inventory Level: 500-1500
3. Click "Get AI-Optimized Price"
4. Should show recommendation from trained model ✓

---

## Part 7: Evaluate Model Performance

### Step 7.1 - Evaluation on Colab

**Cell 6** - Compare with baselines:
```python
from src.evaluate_model import evaluate

results = evaluate()

# Prints comparison:
# RL Agent:           $9,450 (average)
# Static Baseline:    $8,650 (average)
# Improvement:        +9.3%
```

### Step 7.2 - Evaluation Locally

```bash
# Terminal 1 or 2 (stop something first)
python -c "from src.evaluate_model import evaluate; evaluate()"
```

---

## Part 8: Generate Synthetic Data

### On Colab

**Cell 7** - Generate market data:
```python
from src.data_generator import generate_market_data, generate_agent_dataset

# 1. Generate synthetic market data (365 days)
market_data = generate_market_data(num_periods=365)
print(f"✓ Generated {len(market_data)} market data records")

# 2. Generate agent episode dataset
agent_data = generate_agent_dataset(model, num_episodes=100)
print(f"✓ Generated {len(agent_data)} agent episode records")
```

### Download Data

```python
from google.colab import files

files.download('/content/dynamic-pricing-rl/data/sample_market_data.csv')
files.download('/content/dynamic-pricing-rl/data/agent_episodes.csv')
```

---

## Part 9: Complete Workflow Summary

### Local Setup (First Time)
```bash
git clone <url>
cd dynamic-pricing-rl
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mkdir -p models logs checkpoints data
```

### Local Startup (Every Time)
```bash
# Terminal 1
.venv\Scripts\Activate.ps1
uvicorn api.pricing_api:app --reload

# Terminal 2
.venv\Scripts\Activate.ps1
streamlit run dashboard/app.py
```

### Colab Training (One Notebook)
```python
# Cell 1: Clone repo
!git clone <url> /content/dqn-rl
%cd /content/dqn-rl

# Cell 2: Install
!pip install -q torch fastapi streamlit numpy pandas matplotlib

# Cell 3: Train
from src.train_agent import train
model, rewards = train(num_episodes=1000)

# Cell 4: Download
from google.colab import files
files.download('models/dqn_pricing_model_*.pth')
```

### Local Usage
```bash
# 1. Place downloaded model in models/
# 2. Restart API
# 3. Dashboard automatically uses new model
# 4. Test at http://localhost:8501
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Activate venv** | `.venv\Scripts\Activate.ps1` |
| **Start API** | `uvicorn api.pricing_api:app --reload` |
| **Start Dashboard** | `streamlit run dashboard/app.py` |
| **Test API** | `curl http://127.0.0.1:8000/health` |
| **Train (Colab)** | `from src.train_agent import train; train(1000)` |
| **Evaluate** | `python -c "from src.evaluate_model import evaluate; evaluate()"` |

---

## Troubleshooting

### Issue: "No module named src"
**Fix**: Make sure you're in the project root (`dynamic-pricing-rl/`)
```bash
cd dynamic-pricing-rl
python -c "from src.train_agent import train; print('✓')"
```

### Issue: "Port 8000 already in use"
**Fix**: Stop the process or use different port
```bash
# Find process
netstat -ano | findstr :8000
# Kill it or use:
uvicorn api.pricing_api:app --port 8001
```

### Issue: "Model not found" in API
**Fix**: Ensure model file exists
```bash
ls models/
# Should show: dqn_pricing_model_*.pth
```

### Issue: Colab runs out of memory
**Fix**: Use fewer episodes or smaller batch size
```python
from config import TRAINING_CONFIG
TRAINING_CONFIG['batch_size'] = 32  # Reduce
TRAINING_CONFIG['num_episodes'] = 500  # Reduce
```

### Issue: GPU not detected in Colab
**Fix**: Enable GPU in Colab settings
- Menu → Runtime → Change Runtime Type
- Hardware accelerator → GPU (T4 or A100)

---

## Next Steps

1. ✅ Clone and setup locally
2. ✅ Start API + Dashboard
3. ✅ Train on Colab (1000 episodes, ~30 min)
4. ✅ Download model
5. ✅ Place in `models/` folder
6. ✅ Restart API
7. ✅ Test in dashboard
8. ✅ Evaluate performance
9. ✅ Create data artifacts

**Total Time**:
- Local Setup: 5 min
- API/Dashboard: 2 min (always running)
- Colab Training: 30 min (depends on episodes)
- Model Transfer: 2 min
- Testing: 5 min

**Total: ~45 minutes start to finish** 🚀

---

## Tips for Success

✅ Keep Colab notebook saved and indexed  
✅ Download models frequently (Colab resets)  
✅ Use GPU in Colab (much faster training)  
✅ Test API with curl before dashboard  
✅ Keep local `models/` folder backed up  
✅ Monitor Colab resource usage  

---

## File Locations Reference

```
Local Machine:
├── C:\...\dynamic-pricing-rl\
│   ├── models/
│   │   └── dqn_pricing_model_20260304_153045.pth  (download here)
│   ├── logs/
│   ├── checkpoints/
│   ├── src/
│   ├── api/
│   ├── dashboard/
│   ├── config.py
│   └── requirements.txt

Colab:
├── /content/dynamic-pricing-rl/
│   ├── models/
│   │   └── dqn_pricing_model_*.pth  (train here, download)
│   ├── logs/
│   └── ... (same structure)
```

---

**Ready to start? Begin with Part 1!** 🎯
