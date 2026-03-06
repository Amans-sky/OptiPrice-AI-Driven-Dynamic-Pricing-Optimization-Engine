#!/usr/bin/env bash
# Quick Start Script for AI Driven Dynamic Pricing Optimization Engine
# Usage: bash quickstart.sh [action]
# Actions: setup, train, eval, api, dashboard, all

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 AI Driven Dynamic Pricing Optimization Engine"
echo "================================================"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default action
ACTION=${1:-all}

# Setup environment
setup_env() {
    echo -e "${BLUE}[1/4] Creating virtual environment...${NC}"
    if [ ! -d "venv" ]; then
        python -m venv venv
    fi
    
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    
    echo -e "${BLUE}[2/4] Activating virtual environment...${NC}"
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
    
    echo -e "${BLUE}[3/4] Installing dependencies...${NC}"
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo -e "${GREEN}✓ Setup complete!${NC}"
}

# Train model
train_model() {
    echo -e "${BLUE}Training DQN agent...${NC}"
    python run.py
    echo -e "${GREEN}✓ Training complete! Model saved to models/dqn_pricing_model.pth${NC}"
}

# Evaluate model
eval_model() {
    echo -e "${BLUE}Evaluating model performance...${NC}"
    python src/evaluate_model.py
    echo -e "${GREEN}✓ Evaluation complete!${NC}"
}

# Start API
start_api() {
    echo -e "${BLUE}Starting Pricing API on http://127.0.0.1:8000${NC}"
    echo "Press Ctrl+C to stop"
    uvicorn api.pricing_api:app --reload
}

# Start dashboard
start_dashboard() {
    echo -e "${BLUE}Starting Streamlit dashboard on http://localhost:8501${NC}"
    echo "Press Ctrl+C to stop"
    streamlit run dashboard/app.py
}

# Execute based on action
case "$ACTION" in
    setup)
        setup_env
        ;;
    train)
        train_model
        ;;
    eval)
        eval_model
        ;;
    api)
        start_api
        ;;
    dashboard)
        start_dashboard
        ;;
    all)
        setup_env
        echo ""
        train_model
        echo ""
        eval_model
        ;;
    *)
        echo "Unknown action: $ACTION"
        echo "Usage: bash quickstart.sh [action]"
        echo "Actions: setup, train, eval, api, dashboard, all"
        exit 1
        ;;
esac
