"""Visualization utilities for pricing analysis."""

import matplotlib.pyplot as plt
import numpy as np
from src.demand_model import predicted_demand, revenue_function


def plot_price_demand(
    min_price=5,
    max_price=50,
    step=1,
    base_demand=1000.0,
    elasticity=-1.5,
    competitor_price=None,
    show=True,
    save_path=None
):
    """Plot price vs demand and price vs revenue curves.

    Args:
        min_price: Minimum price in range
        max_price: Maximum price in range
        step: Price step size
        base_demand: Base demand parameter
        elasticity: Price elasticity
        competitor_price: Competitor's price (if using relative pricing)
        show: Whether to display the plot
        save_path: Path to save figure (optional)
    """
    prices = np.arange(min_price, max_price + 1, step)
    demands = []
    revenues = []

    for price in prices:
        demand = predicted_demand(price, base_demand, elasticity, competitor_price)
        revenue = price * demand
        demands.append(demand)
        revenues.append(revenue)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Price vs Demand
    axes[0].plot(prices, demands, marker='o', linewidth=2, markersize=6, color='steelblue')
    axes[0].set_xlabel('Price ($)', fontsize=12)
    axes[0].set_ylabel('Demand (units)', fontsize=12)
    axes[0].set_title('Price vs Demand Elasticity', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    # Price vs Revenue
    axes[1].plot(prices, revenues, marker='s', linewidth=2, markersize=6, color='darkgreen')
    optimal_idx = np.argmax(revenues)
    optimal_price = prices[optimal_idx]
    optimal_revenue = revenues[optimal_idx]
    axes[1].scatter([optimal_price], [optimal_revenue], color='red', s=200, zorder=5, label=f'Optimal: ${optimal_price}')
    axes[1].set_xlabel('Price ($)', fontsize=12)
    axes[1].set_ylabel('Revenue ($)', fontsize=12)
    axes[1].set_title('Price vs Revenue (Optimization Target)', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=11)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig


def plot_competitor_comparison(
    prices=None,
    competitor_price=25.0,
    show=True,
    save_path=None
):
    """Plot revenue comparison at different competitor prices.

    Args:
        prices: List of prices to evaluate (default: 5-50)
        competitor_price: Competitor's reference price
        show: Whether to display the plot
        save_path: Path to save figure (optional)
    """
    if prices is None:
        prices = np.arange(5, 51, 2.5)

    competitor_prices = [10.0, 20.0, 25.0, 30.0, 40.0]
    fig, ax = plt.subplots(figsize=(12, 6))

    for cp in competitor_prices:
        revenues = [revenue_function(p, competitor_price=cp) for p in prices]
        label = f'Competitor: ${cp}' + (' (YOUR REF)' if cp == competitor_price else '')
        ax.plot(prices, revenues, marker='o', label=label, linewidth=2, markersize=6)

    ax.set_xlabel('Your Price ($)', fontsize=12)
    ax.set_ylabel('Expected Revenue ($)', fontsize=12)
    ax.set_title('Revenue vs Competitor Pricing Strategy', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig


def plot_training_progress(episode_rewards, window=10, show=True, save_path=None):
    """Plot training progress with moving average.

    Args:
        episode_rewards: List of rewards per episode
        window: Moving average window size
        show: Whether to display the plot
        save_path: Path to save figure (optional)
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    episodes = np.arange(len(episode_rewards))
    ax.plot(episodes, episode_rewards, alpha=0.3, color='blue', label='Episode Reward')

    # Moving average
    if len(episode_rewards) >= window:
        moving_avg = np.convolve(episode_rewards, np.ones(window)/window, mode='valid')
        ax.plot(np.arange(window-1, len(episode_rewards)), moving_avg, linewidth=2.5, color='darkblue', label=f'Moving Average (window={window})')

    ax.set_xlabel('Episode', fontsize=12)
    ax.set_ylabel('Total Reward ($)', fontsize=12)
    ax.set_title('DQN Training Progress', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig
