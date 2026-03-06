"""Configuration for DQN training and evaluation.

This module centralizes all hyperparameters and settings,
making the project reproducible and easy to modify.
"""

from pathlib import Path
import torch

# Base directory for relative paths
BASE_DIR = Path(__file__).resolve().parent

# ============================================================================
# TRAINING CONFIGURATION
# ============================================================================

TRAINING_CONFIG = {
    # Episode control
    "num_episodes": 1000,
    "max_steps_per_episode": 50,

    # DQN hyperparameters
    "gamma": 0.99,  # Discount factor (0-1, higher = long-term focused)
    "learning_rate": 1e-3,  # Optimizer learning rate
    "batch_size": 64,  # Mini-batch size for training

    # Exploration (Epsilon-Greedy)
    "epsilon_start": 1.0,  # Initial exploration rate
    "epsilon_end": 0.1,  # Final (minimum) exploration rate
    "epsilon_decay": 0.995,  # Decay factor per episode

    # Replay Buffer
    "replay_buffer_capacity": 10000,
    "min_buffer_size": 64,  # Minimum samples before training starts

    # Target Network
    "target_update_frequency": 10,  # Update target network every N episodes

    # Random seed for reproducibility
    "seed": 42,

    # Logging
    "log_frequency": 10,  # Print stats every N episodes
    "save_frequency": 50,  # Save model every N episodes
}

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

ENVIRONMENT_CONFIG = {
    "price_min": 5,
    "price_max": 50,
    "price_step": 5,
    "base_demand": 1000.0,
    "elasticity": -1.5,
    "competitor_price_init": 25.0,
    "competitor_price_range": (10.0, 40.0),
    "inventory_init": 1000.0,
}

# ============================================================================
# EVALUATION CONFIGURATION
# ============================================================================

EVALUATION_CONFIG = {
    "num_episodes": 50,
    "static_baseline_price": 20.0,  # Fixed price for baseline comparison
}

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_CONFIG = {
    "host": "0.0.0.0",  # Listen on all interfaces (Docker-friendly)
    "port": 8000,
    "reload": True,
    "api_url": "http://127.0.0.1:8000",
    "default_demand_level": 100.0,
    "default_competitor_price": 25.0,
    "default_inventory_level": 1000.0,
    "request_timeout": 5.0,
}

# ============================================================================
# PATHS (Using pathlib for cross-platform compatibility)
# ============================================================================

PATHS = {
    "model_dir": BASE_DIR / "models",
    "data_dir": BASE_DIR / "data",
    "log_dir": BASE_DIR / "logs",
    "checkpoint_dir": BASE_DIR / "checkpoints",
}

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

MODEL_CONFIG = {
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "save_with_timestamp": True,  # Save models with timestamp
    "keep_best_model": True,  # Save best performing model
    "model_name": "dqn_pricing_model",
    "extension": ".pth",
}
