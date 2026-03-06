"""Evaluate trained DQN agent vs baseline strategies."""

import os
import sys
import logging
import torch
import numpy as np
import glob

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment import PricingEnvironment
from src.dqn_agent import DQN
from config import EVALUATION_CONFIG, PATHS, ENVIRONMENT_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_latest_model():
    """Find the most recent model file in the models directory.
    
    Returns:
        Path to latest model, or None if no models found
    """
    model_files = glob.glob(os.path.join(PATHS['model_dir'], 'dqn_pricing_model_*.pth'))
    if not model_files:
        return None
    return max(model_files, key=os.path.getctime)


def load_model(model_path=None):
    """Load DQN model from disk.
    
    Args:
        model_path: Path to model file. If None, finds latest model.
        
    Returns:
        Loaded DQN model
    """
    if model_path is None:
        model_path = find_latest_model()
    
    if not model_path or not os.path.exists(model_path):
        logger.error(f"Model not found. Train first.")
        return None
    
    state_size = 3  # [demand_level, competitor_price, inventory_level]
    action_size = 10  # 10 price levels
    
    model = DQN(state_size, action_size)
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    
    logger.info(f"Model loaded from: {model_path}")
    return model


def evaluate_rl_agent(model, num_episodes=None):
    """Evaluate RL agent performance.
    
    Args:
        model: Trained DQN model
        num_episodes: Number of episodes to evaluate
        
    Returns:
        Array of episode rewards
    """
    num_episodes = num_episodes or EVALUATION_CONFIG['num_episodes']
    env = PricingEnvironment(max_steps=ENVIRONMENT_CONFIG['max_steps_per_episode'])
    
    episode_rewards = []
    
    for episode in range(num_episodes):
        state = env.reset()
        done = False
        episode_reward = 0.0
        
        while not done:
            state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                q_values = model(state_t)
            action = torch.argmax(q_values).item()
            state, reward, done, _ = env.step(action)
            episode_reward += reward
        
        episode_rewards.append(episode_reward)
    
    return np.array(episode_rewards)


def evaluate_baseline_strategy(strategy='static', baseline_price=None, num_episodes=None):
    """Evaluate baseline pricing strategy.
    
    Args:
        strategy: 'static' (fixed price) or 'random' (random prices)
        baseline_price: Price to use for static strategy
        num_episodes: Number of episodes to evaluate
        
    Returns:
        Array of episode rewards
    """
    num_episodes = num_episodes or EVALUATION_CONFIG['num_episodes']
    baseline_price = baseline_price or EVALUATION_CONFIG['static_baseline_price']
    
    env = PricingEnvironment(max_steps=ENVIRONMENT_CONFIG['max_steps_per_episode'])
    episode_rewards = []
    
    for episode in range(num_episodes):
        state = env.reset()
        done = False
        episode_reward = 0.0
        
        while not done:
            if strategy == 'static':
                # Use fixed baseline price
                price = baseline_price
                demand = env.demand_function(price)
                revenue = price * demand
                episode_reward += revenue
                _, _, done, _ = env.step(0)  # dummy action
            elif strategy == 'random':
                # Use random action
                action = np.random.randint(0, len(env.price_levels))
                state, reward, done, _ = env.step(action)
                episode_reward += reward
        
        episode_rewards.append(episode_reward)
    
    return np.array(episode_rewards)


def evaluate(model_path=None):
    """Evaluate trained model and compare with baselines.
    
    Args:
        model_path: Path to saved model (uses latest if None)
    """
    logger.info("=" * 70)
    logger.info("Starting Model Evaluation")
    logger.info("=" * 70)
    
    # Load model
    model = load_model(model_path)
    if model is None:
        return
    
    num_episodes = EVALUATION_CONFIG['num_episodes']
    
    # Evaluate strategies
    logger.info(f"Evaluating RL agent ({num_episodes} episodes)...")
    rl_rewards = evaluate_rl_agent(model, num_episodes)
    
    logger.info(f"Evaluating static baseline (${EVALUATION_CONFIG['static_baseline_price']:.0f})...")
    static_rewards = evaluate_baseline_strategy('static', num_episodes=num_episodes)
    
    logger.info(f"Evaluating random baseline...")
    random_rewards = evaluate_baseline_strategy('random', num_episodes=num_episodes)
    
    # Compute statistics
    rl_mean = np.mean(rl_rewards)
    rl_std = np.std(rl_rewards)
    static_mean = np.mean(static_rewards)
    static_std = np.std(static_rewards)
    random_mean = np.mean(random_rewards)
    random_std = np.std(random_rewards)
    
    improvement_vs_static = ((rl_mean - static_mean) / abs(static_mean)) * 100
    improvement_vs_random = ((rl_mean - random_mean) / abs(random_mean)) * 100
    
    # Display results
    logger.info("\n" + "=" * 70)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 70)
    logger.info(f"\nRL Agent:")
    logger.info(f"  Mean Reward:     ${rl_mean:10,.2f}")
    logger.info(f"  Std Dev:         ${rl_std:10,.2f}")
    logger.info(f"  Min/Max:         ${np.min(rl_rewards):10,.2f} / ${np.max(rl_rewards):10,.2f}")
    
    logger.info(f"\nStatic Baseline (${EVALUATION_CONFIG['static_baseline_price']:.0f}):")
    logger.info(f"  Mean Reward:     ${static_mean:10,.2f}")
    logger.info(f"  Std Dev:         ${static_std:10,.2f}")
    logger.info(f"  Min/Max:         ${np.min(static_rewards):10,.2f} / ${np.max(static_rewards):10,.2f}")
    
    logger.info(f"\nRandom Baseline:")
    logger.info(f"  Mean Reward:     ${random_mean:10,.2f}")
    logger.info(f"  Std Dev:         ${random_std:10,.2f}")
    logger.info(f"  Min/Max:         ${np.min(random_rewards):10,.2f} / ${np.max(random_rewards):10,.2f}")
    
    logger.info(f"\nImprovement:")
    logger.info(f"  vs Static:       {improvement_vs_static:+.2f}%")
    logger.info(f"  vs Random:       {improvement_vs_random:+.2f}%")
    logger.info("=" * 70)
    
    return {
        'rl': {'mean': rl_mean, 'std': rl_std, 'rewards': rl_rewards},
        'static': {'mean': static_mean, 'std': static_std, 'rewards': static_rewards},
        'random': {'mean': random_mean, 'std': random_std, 'rewards': random_rewards},
    }


if __name__ == '__main__':
    evaluate()
