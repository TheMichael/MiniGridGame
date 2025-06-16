#!/usr/bin/env python3
"""
D3QN Agent implementation for AI Agent Galaxy.
Extracted from original app.py - Dueling Double Deep Q-Network agent.
"""
import random
import numpy as np
import torch
import torch.nn as nn

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DuelingQNetwork(nn.Module):
    """Dueling Q-Network for D3QN agent."""
    
    def __init__(self, input_shape, action_size, seed):
        super(DuelingQNetwork, self).__init__()
        self.seed = torch.manual_seed(seed)
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU()
        )
        self.conv_output_size = self._get_conv_output_size(input_shape)
        self.fc_value = nn.Sequential(
            nn.Linear(self.conv_output_size, 512),
            nn.ReLU(),
            nn.Linear(512, 1)
        )
        self.fc_advantage = nn.Sequential(
            nn.Linear(self.conv_output_size, 512),
            nn.ReLU(),
            nn.Linear(512, action_size)
        )

    def _get_conv_output_size(self, shape):
        o = self.conv_layers(torch.zeros(1, *shape))
        return int(np.prod(o.size()))

    def forward(self, state):
        x = self.conv_layers(state)
        x = x.view(x.size(0), -1)
        value = self.fc_value(x)
        advantage = self.fc_advantage(x)
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        return q_values


class D3QNAgent:
    """Dueling Double Deep Q-Network Agent for MiniGrid navigation."""
    
    def __init__(self, input_shape, action_size, seed):
        self.state_size = input_shape
        self.action_size = action_size
        self.seed = random.seed(seed)
        self.valid_actions = [0, 1, 2, 5]
        self.qnetwork_local = DuelingQNetwork(input_shape, action_size, seed).to(device)

    def act(self, state, eps=0.):
        state = torch.from_numpy(state).float().unsqueeze(0).to(device)
        self.qnetwork_local.eval()
        with torch.no_grad():
            action_values = self.qnetwork_local(state)
            mask = torch.ones_like(action_values) * float('-inf')
            for a in self.valid_actions:
                if a < action_values.shape[1]:
                    mask[0, a] = 0
            masked_action_values = action_values + mask
        self.qnetwork_local.train()
        
        if random.random() > eps:
            return np.argmax(masked_action_values.cpu().data.numpy())
        else:
            return random.choice(self.valid_actions)