"""Experience Replay Buffer for DQN training.

The replay buffer stores transitions and samples random mini-batches
for training. This breaks temporal correlations and improves stability.
"""

import random
from collections import deque
import numpy as np
import torch


class ReplayBuffer:
    """Circular buffer for storing and sampling experience transitions.
    
    Attributes:
        capacity: Maximum number of transitions to store
        memory: Deque of (state, action, reward, next_state, done) tuples
    """

    def __init__(self, capacity=10000):
        """Initialize replay buffer.
        
        Args:
            capacity: Maximum number of transitions to store
        """
        self.memory = deque(maxlen=capacity)
        self.capacity = capacity

    def push(self, state, action, reward, next_state, done):
        """Store a transition in the replay buffer.
        
        Args:
            state: Current state (numpy array)
            action: Action taken (int)
            reward: Reward received (float)
            next_state: Next state (numpy array)
            done: Whether episode terminated (bool)
        """
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        """Sample a random mini-batch from the replay buffer.
        
        Args:
            batch_size: Number of transitions to sample
            
        Returns:
            Tuple of (states, actions, rewards, next_states, dones) as tensors
        """
        if len(self.memory) < batch_size:
            raise ValueError(f"Buffer has {len(self.memory)} samples but batch_size={batch_size}")

        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        return (
            torch.tensor(np.array(states), dtype=torch.float32),
            torch.tensor(np.array(actions), dtype=torch.long),
            torch.tensor(np.array(rewards), dtype=torch.float32),
            torch.tensor(np.array(next_states), dtype=torch.float32),
            torch.tensor(np.array(dones), dtype=torch.float32)
        )

    def __len__(self):
        """Return current number of transitions in buffer."""
        return len(self.memory)

    def is_ready(self, batch_size):
        """Check if buffer has enough samples for training.
        
        Args:
            batch_size: Required batch size
            
        Returns:
            True if buffer has at least batch_size samples
        """
        return len(self.memory) >= batch_size
