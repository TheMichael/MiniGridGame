#!/usr/bin/env python3
"""
DDQN Agent implementation for AI Agent Galaxy.
Extracted from original app.py - Double Deep Q-Network agent.
"""
import random
import numpy as np
import torch
import torch.nn as nn

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DoubleDQNNetwork(nn.Module):
    """Double Deep Q-Network for DDQN agent."""
    
    def __init__(self, input_shape, num_actions):
        super(DoubleDQNNetwork, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU()
        )
        conv_out_size = self.get_conv_out(input_shape)
        self.fc = nn.Sequential(
            nn.Linear(conv_out_size, 512),
            nn.ReLU(),
            nn.Linear(512, num_actions)
        )

    def get_conv_out(self, shape):
        o = self.conv(torch.zeros(1, *shape))
        return int(np.prod(o.size()))

    def forward(self, x):
        conv_out = self.conv(x)
        conv_out = conv_out.view(conv_out.size()[0], -1)
        return self.fc(conv_out)


class DDQNAgent:
    """Double Deep Q-Network Agent for MiniGrid navigation."""
    
    def __init__(self, input_shape, num_actions):
        self.num_actions = num_actions
        self.device = device
        self.allowed_actions = [a for a in range(num_actions) if a not in [3, 4, 6]]
        self.allowed_mask = torch.zeros(num_actions, dtype=torch.bool, device=self.device)
        for a in self.allowed_actions:
            self.allowed_mask[a] = True
        self.policy_net = DoubleDQNNetwork(input_shape, num_actions).to(self.device)
        self.policy_net.eval()

    def select_action(self, state, current_eps):
        if random.random() < current_eps:
            return random.choice(self.allowed_actions)
        else:
            with torch.no_grad():
                state = state.to(self.device)
                q_values = self.policy_net(state)
                q_values[0, ~self.allowed_mask] = -float("inf")
                return int(q_values.max(1)[1].item())