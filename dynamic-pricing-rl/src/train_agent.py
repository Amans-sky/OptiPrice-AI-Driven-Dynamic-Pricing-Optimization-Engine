"""Training loop for DQN agent with experience replay and target networks."""

import os
import sys
import logging
from datetime import datetime
import random
import torch
import torch.nn.functional as F
from torch import optim
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dqn_agent import DQN
from src.environment import PricingEnvironment
from src.replay_buffer import ReplayBuffer
from src.visualization import plot_training_progress
from config import TRAINING_CONFIG, ENVIRONMENT_CONFIG, PATHS, MODEL_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs(PATHS['model_dir'], exist_ok=True)
os.makedirs(PATHS['checkpoint_dir'], exist_ok=True)
os.makedirs(PATHS['log_dir'], exist_ok=True)


def set_seed(seed):
    """Set random seeds for reproducibility.
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    logger.info(f"Random seed set to {seed}")


def get_model_path(timestamp=True):
    """Generate model save path with optional timestamp.
    
    Args:
        timestamp: Whether to include timestamp in filename
        
    Returns:
        Path to model file
    """
    model_name = MODEL_CONFIG['model_name']
    extension = MODEL_CONFIG['extension']
    
    if timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model_name}_{ts}{extension}"
    else:
        filename = f"{model_name}{extension}"
    
    return os.path.join(PATHS['model_dir'], filename)


def train(num_episodes=None, lr=None):
    """Train DQN agent with experience replay and target networks.
    
    Args:
        num_episodes: Number of training episodes (uses config if None)
        lr: Learning rate (uses config if None)
        
    Returns:
        Trained DQN model and episode rewards history
    """
    # Use config values if not provided
    num_episodes = num_episodes or TRAINING_CONFIG['num_episodes']
    lr = lr or TRAINING_CONFIG['learning_rate']
    
    # Set random seed for reproducibility
    set_seed(TRAINING_CONFIG['seed'])
    
    logger.info("=" * 70)
    logger.info("Starting DQN Training")
    logger.info("=" * 70)
    logger.info(f"Episodes: {num_episodes}")
    logger.info(f"Learning Rate: {lr}")
    logger.info(f"Batch Size: {TRAINING_CONFIG['batch_size']}")
    logger.info(f"Gamma (discount): {TRAINING_CONFIG['gamma']}")
    logger.info(f"Epsilon Decay: {TRAINING_CONFIG['epsilon_decay']}")
    
    # Initialize environment and agent
    env = PricingEnvironment(max_steps=TRAINING_CONFIG['max_steps_per_episode'])
    state_size = 3  # [demand_level, competitor_price, inventory_level]
    action_size = len(env.price_levels)
    
    # Create policy and target networks
    policy_net = DQN(state_size, action_size)
    target_net = DQN(state_size, action_size)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()  # Target net in evaluation mode
    
    optimizer = optim.Adam(policy_net.parameters(), lr=lr)
    replay_buffer = ReplayBuffer(capacity=TRAINING_CONFIG['replay_buffer_capacity'])
    
    # Exploration parameters
    epsilon = TRAINING_CONFIG['epsilon_start']
    epsilon_end = TRAINING_CONFIG['epsilon_end']
    epsilon_decay = TRAINING_CONFIG['epsilon_decay']
    
    # Track metrics
    episode_rewards = []
    episode_lengths = []
    episode_losses = []
    epsilon_values = []
    best_reward = float('-inf')
    
    logger.info(f"Environment: state_size={state_size}, action_size={action_size}")
    logger.info(f"Replay Buffer: capacity={TRAINING_CONFIG['replay_buffer_capacity']}")
    logger.info("Starting training loop...")
    
    for episode in range(num_episodes):
        state = env.reset()
        episode_reward = 0.0
        episode_loss = 0.0
        step = 0
        done = False
        
        # Episode loop
        while not done:
            # Select action with epsilon-greedy
            state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            
            if random.random() < epsilon:
                action = random.randrange(action_size)  # Explore
            else:
                with torch.no_grad():
                    q_values = policy_net(state_t)
                    action = torch.argmax(q_values).item()  # Exploit
            
            # Take action in environment
            next_state, reward, done, info = env.step(action)
            episode_reward += reward
            
            # Store transition in replay buffer
            replay_buffer.push(state, action, reward, next_state, done)
            
            # Train on mini-batch if buffer is ready
            if replay_buffer.is_ready(TRAINING_CONFIG['batch_size']):
                states, actions, rewards, next_states, dones = replay_buffer.sample(
                    TRAINING_CONFIG['batch_size']
                )
                
                # Compute Q-learning target
                with torch.no_grad():
                    max_next_q = target_net(next_states).max(1)[0]
                    target_q = rewards + TRAINING_CONFIG['gamma'] * max_next_q * (1 - dones)
                
                # Compute current Q-values
                current_q = policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
                
                # Loss and optimization
                loss = F.smooth_l1_loss(current_q, target_q)
                episode_loss += loss.item()
                
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(policy_net.parameters(), max_norm=1.0)
                optimizer.step()
            
            state = next_state
            step += 1
        
        # Decay epsilon
        epsilon = max(epsilon_end, epsilon * epsilon_decay)
        episode_rewards.append(episode_reward)
        episode_lengths.append(step)
        if episode_loss > 0:
            episode_losses.append(episode_loss / max(step, 1))
        epsilon_values.append(epsilon)
        
        # Update target network periodically
        if (episode + 1) % TRAINING_CONFIG['target_update_frequency'] == 0:
            target_net.load_state_dict(policy_net.state_dict())
        
        # Log progress
        if (episode + 1) % TRAINING_CONFIG['log_frequency'] == 0:
            avg_reward = np.mean(episode_rewards[-TRAINING_CONFIG['log_frequency']:])
            logger.info(
                f"Episode {episode+1:4d}/{num_episodes}  |  "
                f"Reward: {episode_reward:8.2f}  |  "
                f"Avg (last {TRAINING_CONFIG['log_frequency']}): {avg_reward:8.2f}  |  "
                f"Epsilon: {epsilon:.3f}"
            )
        
        # Save checkpoint
        if (episode + 1) % TRAINING_CONFIG['save_frequency'] == 0:
            ckpt_path = os.path.join(PATHS['checkpoint_dir'], f"ckpt_ep{episode+1}.pth")
            torch.save(policy_net.state_dict(), ckpt_path)
            logger.debug(f"Checkpoint saved: {ckpt_path}")
    
    # Save final model
    model_path = get_model_path(timestamp=MODEL_CONFIG['save_with_timestamp'])
    torch.save(policy_net.state_dict(), model_path)
    logger.info(f"✓ Training complete! Model saved to: {model_path}")
    logger.info(f"✓ Final reward: {episode_rewards[-1]:.2f}")
    logger.info(f"✓ Best reward: {max(episode_rewards):.2f}")
    logger.info(f"✓ Average reward (last 10): {np.mean(episode_rewards[-10:]):.2f}")
    
    # Generate visualizations
    plot_training_progress(episode_rewards)
    
    return policy_net, episode_rewards


if __name__ == '__main__':
    model, rewards = train()
    logger.info("Training script completed successfully.")
