#!/usr/bin/env python3
"""
MiniGrid environment setup for AI Agent Galaxy.
Extracted from original app.py - handles environment creation and preprocessing.
"""
import cv2
import numpy as np
import gymnasium as gym
import minigrid
from minigrid.wrappers import RGBImgObsWrapper, RGBImgPartialObsWrapper, ImgObsWrapper


def preprocess_state(state):
    """Preprocess state for neural network input."""
    state = cv2.cvtColor(state, cv2.COLOR_RGB2GRAY)
    state = np.expand_dims(state, axis=0)
    return state.astype(np.float32)


def setup_environment():
    """Create and configure MiniGrid environment."""
    ENV_NAME = "MiniGrid-MultiRoom-N6-v0"
    env = gym.make(ENV_NAME, render_mode="rgb_array", highlight=False)
    env = RGBImgPartialObsWrapper(env)
    env = ImgObsWrapper(env)
    return env