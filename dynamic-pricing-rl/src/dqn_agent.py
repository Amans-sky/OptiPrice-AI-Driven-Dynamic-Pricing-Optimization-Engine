import torch
import torch.nn as nn


class DQN(nn.Module):
    """Deep Q Network for pricing policy.
    
    Input: state_size (number of features)
    Output: action_size (number of discrete price actions)
    """
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_size)
        )

    def forward(self, x):
        return self.network(x)
