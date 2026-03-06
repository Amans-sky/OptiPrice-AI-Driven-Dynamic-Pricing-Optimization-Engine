"""Training visualization and analysis utilities."""

import numpy as np
import matplotlib.pyplot as plt
import os
import logging
from config import PATHS

logger = logging.getLogger(__name__)


def plot_training_progress(episode_rewards, save_path=None):
    """Plot training progress with moving average.
    
    Args:
        episode_rewards: List of rewards per episode
        save_path: Path to save figure (uses default if None)
    """
    if save_path is None:
        save_path = os.path.join(PATHS['log_dir'], 'training_progress.png')
    
    os.makedirs(PATHS['log_dir'], exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    episodes = np.arange(len(episode_rewards))
    
    # Plot raw episode rewards
    ax.plot(episodes, episode_rewards, alpha=0.3, color='steelblue', 
            linewidth=1.5, label='Episode Reward')
    
    # Plot moving averages
    windows = [10, 50]
    colors = ['darkblue', 'navy']
    
    for window, color in zip(windows, colors):
        if len(episode_rewards) >= window:
            moving_avg = np.convolve(episode_rewards, np.ones(window)/window, 
                                     mode='valid')
            ax.plot(np.arange(window-1, len(episode_rewards)), moving_avg,
                    linewidth=2.5, color=color, label=f'MA(n={window})')
    
    # Styling
    ax.set_xlabel('Episode', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Reward ($)', fontsize=12, fontweight='bold')
    ax.set_title('DQN Training Progress - Episode Rewards', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='lower right')
    
    # Add statistics to plot
    final_avg = np.mean(episode_rewards[-50:]) if len(episode_rewards) >= 50 else np.mean(episode_rewards)
    ax.axhline(y=final_avg, color='red', linestyle='--', alpha=0.5, linewidth=2,
               label=f'Final Avg: ${final_avg:.0f}')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    logger.info(f"✓ Training plot saved: {save_path}")
    plt.close()


def plot_training_comparison(train_rewards, eval_rewards, save_path=None):
    """Compare training vs evaluation rewards.
    
    Args:
        train_rewards: Training episode rewards
        eval_rewards: Evaluation episode rewards
        save_path: Path to save figure
    """
    if save_path is None:
        save_path = os.path.join(PATHS['log_dir'], 'train_eval_comparison.png')
    
    os.makedirs(PATHS['log_dir'], exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Training progress
    episodes = np.arange(len(train_rewards))
    ax1.plot(episodes, train_rewards, alpha=0.4, color='steelblue', label='Episode')
    
    if len(train_rewards) >= 10:
        ma10 = np.convolve(train_rewards, np.ones(10)/10, mode='valid')
        ax1.plot(np.arange(9, len(train_rewards)), ma10, linewidth=2.5, 
                color='darkblue', label='MA(10)')
    
    ax1.set_xlabel('Episode', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Reward ($)', fontsize=11, fontweight='bold')
    ax1.set_title('Training Progress', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Evaluation comparison
    strategies = ['RL Agent', 'Static Baseline', 'Random Baseline']
    colors_box = ['steelblue', 'orange', 'gray']
    
    if len(eval_rewards) == 3:
        data = [eval_rewards[0], eval_rewards[1], eval_rewards[2]]
        ax2.boxplot(data, labels=strategies, patch_artist=True)
        
        for patch, color in zip(ax2.artists, colors_box):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    
    ax2.set_ylabel('Total Reward ($)', fontsize=11, fontweight='bold')
    ax2.set_title('Evaluation Results - Strategy Comparison', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    logger.info(f"✓ Comparison plot saved: {save_path}")
    plt.close()


def plot_q_value_heatmap(q_values_history, save_path=None):
    """Plot Q-value evolution heatmap across actions.
    
    Args:
        q_values_history: List of Q-value arrays from episodes
        save_path: Path to save figure
    """
    if save_path is None:
        save_path = os.path.join(PATHS['log_dir'], 'q_values_heatmap.png')
    
    os.makedirs(PATHS['log_dir'], exist_ok=True)
    
    # Sample every Nth episode to reduce data size
    sample_rate = max(1, len(q_values_history) // 100)
    sampled_history = q_values_history[::sample_rate]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create heatmap
    if len(sampled_history) > 0:
        data = np.array(sampled_history)
        im = ax.imshow(data.T, aspect='auto', cmap='viridis', interpolation='nearest')
        
        ax.set_xlabel('Episode (sampled)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Action (Price Level)', fontsize=11, fontweight='bold')
        ax.set_title('Q-Value Evolution Across Actions', fontsize=12, fontweight='bold')
        
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Q-Value', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    logger.info(f"✓ Q-value heatmap saved: {save_path}")
    plt.close()


def plot_episode_stats(episodes_stats, save_path=None):
    """Plot episode statistics (reward, length, loss).
    
    Args:
        episodes_stats: Dict with 'rewards', 'lengths', 'losses' lists
        save_path: Path to save figure
    """
    if save_path is None:
        save_path = os.path.join(PATHS['log_dir'], 'episode_stats.png')
    
    os.makedirs(PATHS['log_dir'], exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Rewards
    if 'rewards' in episodes_stats:
        ax = axes[0, 0]
        rewards = episodes_stats['rewards']
        ax.plot(rewards, alpha=0.6, color='steelblue', linewidth=1)
        if len(rewards) >= 10:
            ma = np.convolve(rewards, np.ones(10)/10, mode='valid')
            ax.plot(np.arange(9, len(rewards)), ma, color='darkblue', linewidth=2.5)
        ax.set_ylabel('Episode Reward', fontsize=11, fontweight='bold')
        ax.set_title('Episode Rewards', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    # Loss
    if 'losses' in episodes_stats:
        ax = axes[0, 1]
        losses = episodes_stats['losses']
        ax.plot(losses, alpha=0.6, color='coral', linewidth=1)
        ax.set_ylabel('Loss', fontsize=11, fontweight='bold')
        ax.set_title('Training Loss', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
    
    # Episode Length
    if 'lengths' in episodes_stats:
        ax = axes[1, 0]
        lengths = episodes_stats['lengths']
        ax.hist(lengths, bins=20, alpha=0.7, color='green', edgecolor='black')
        ax.set_xlabel('Episode Length (steps)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax.set_title('Episode Length Distribution', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    # Epsilon decay (if available)
    if 'epsilon' in episodes_stats:
        ax = axes[1, 1]
        epsilon_vals = episodes_stats['epsilon']
        ax.plot(epsilon_vals, color='purple', linewidth=2)
        ax.set_xlabel('Episode', fontsize=11, fontweight='bold')
        ax.set_ylabel('Epsilon', fontsize=11, fontweight='bold')
        ax.set_title('Exploration Rate Decay', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.05])
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    logger.info(f"✓ Episode stats plot saved: {save_path}")
    plt.close()
