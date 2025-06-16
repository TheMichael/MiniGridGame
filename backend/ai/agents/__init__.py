"""
AI agents for AI Agent Galaxy.
Contains DDQN and D3QN agent implementations.
"""

from .ddqn_agent import DDQNAgent, DoubleDQNNetwork
from .d3qn_agent import D3QNAgent, DuelingQNetwork

__all__ = ['DDQNAgent', 'DoubleDQNNetwork', 'D3QNAgent', 'DuelingQNetwork']