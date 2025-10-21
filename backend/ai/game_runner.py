#!/usr/bin/env python3
"""
Game execution logic for AI Agent Galaxy.
Extracted from original app.py - handles running episodes and generating videos.
"""
import os
import torch
import numpy as np
import imageio
from .environment import setup_environment, preprocess_state
from .agents.ddqn_agent import DDQNAgent, DoubleDQNNetwork
from .agents.d3qn_agent import D3QNAgent

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Constants
MAX_STEPS = 120


def shape_reward(step_count, max_steps, done, truncated, states_list, current_state, actions_list):
    """Reward function for DDQN agent."""
    reward = -0.5
    if actions_list[-1] == 5 and not np.array_equal(states_list[-1], current_state):
        reward += 5
    if actions_list[-1] == 5 and np.array_equal(states_list[-1], current_state):
        reward -= 3
    if len(actions_list) >= 2 and actions_list[-1] == 5 and actions_list[-2] == 5:
        reward -= 3
    if np.array_equal(states_list[-1], current_state):
        reward -= 4
    if done:
        reward += 80 + 10*(1 - 0.9 * (step_count / max_steps))
    if truncated or step_count == max_steps:
        reward -= 10
    return reward


def compute_reward(step_count, max_steps, done, truncated, states_list, current_state, actions_list):
    """Reward function for D3QN agent."""
    reward = -0.5
    if actions_list[-1] == 5 and not np.array_equal(states_list[-1], current_state):
        reward += 8
    if actions_list[-1] == 5 and np.array_equal(states_list[-1], current_state):
        reward -= 3
    if len(actions_list) >= 2 and actions_list[-1] == 5 and actions_list[-2] == 5:
        reward -= 3
    if np.array_equal(states_list[-1], current_state):
        reward -= 4
    if done:
        reward += 25 + 10*(1 - 0.9 * (step_count / max_steps))
    if truncated or step_count == max_steps:
        reward -= 10
    return reward


def video_of_one_DDQN_episode(env, policy_network_path, gif_filename):
    """Run one episode with DDQN agent and generate video."""
    obs, _ = env.reset()
    obs = preprocess_state(obs)
    input_shape = obs.shape
    num_actions = env.action_space.n
    policy_net = DoubleDQNNetwork(input_shape, num_actions)
    
    try:
        policy_net.load_state_dict(torch.load(policy_network_path, map_location=device))
    except FileNotFoundError:
        return 0, 120, []

    policy_net.to(device)
    policy_net.eval()
    agent = DDQNAgent(input_shape, num_actions)
    agent.policy_net = policy_net
    
    total_reward = 0
    frames = []
    steps_log = []
    obs, _ = env.reset()
    processed = preprocess_state(obs)
    state = torch.tensor(processed, dtype=torch.float32).unsqueeze(0)
    episode_states = []
    episode_actions = []

    for t in range(MAX_STEPS):
        action = agent.select_action(state, 0)
        episode_states.append(state)
        episode_actions.append(action)
        
        next_obs, _, done, truncated, _ = env.step(action)
        reward = shape_reward(t, MAX_STEPS, done, truncated, episode_states, next_obs, episode_actions)
        total_reward += reward
        
        step_info = {
            'step': int(t + 1),
            'action': int(action),
            'reward': float(reward),
            'done': bool(done),
            'truncated': bool(truncated),
            'result': 'Goal reached!' if done else ('Max steps reached' if truncated else 'Continuing...')
        }
        steps_log.append(step_info)
        
        processed_next = preprocess_state(next_obs)
        state = torch.tensor(processed_next, dtype=torch.float32).unsqueeze(0)

        try:
            frame = env.render()
            if frame.shape[-1] == 3:
                frames.append(frame)
        except Exception as e:
            print(f"Rendering error: {e}")
        
        if done or truncated:
            break

    try:
        imageio.mimsave(gif_filename, frames, duration=0.1, loop=0)
    except Exception as e:
        print(f"GIF save error: {e}")
        return float(total_reward), int(t + 1), None, steps_log
    
    return float(total_reward), int(t + 1), gif_filename, steps_log


def video_of_one_D3QN_episode(env, policy_network_path, gif_filename):
    """Run one episode with D3QN agent and generate video."""
    trained_agent = D3QNAgent((1, 56, 56), env.action_space.n, seed=0)
    
    try:
        trained_agent.qnetwork_local.load_state_dict(torch.load(policy_network_path, map_location=device))
    except FileNotFoundError:
        return 0, 120, []
    
    trained_agent.qnetwork_local.eval()
    score = 0
    frames = []
    steps_log = []
    state, _ = env.reset()
    state = preprocess_state(state)
    episode_states = []
    episode_actions = []

    for t in range(MAX_STEPS):
        action = trained_agent.act(state, 0.0)
        episode_states.append(state)
        episode_actions.append(action)

        current_state, _, done, truncated, _ = env.step(action)
        current_state = preprocess_state(current_state)
        reward = compute_reward(t, MAX_STEPS, done, truncated, episode_states, current_state, episode_actions)
        
        step_info = {
            'step': int(t + 1),
            'action': int(action),
            'reward': float(reward),
            'done': bool(done),
            'truncated': bool(truncated),
            'result': 'Goal reached!' if done else ('Max steps reached' if truncated else 'Continuing...')
        }
        steps_log.append(step_info)

        state = current_state
        score += reward
        
        try:
            frame = env.render()
            if frame.shape[-1] == 3:
                frames.append(frame)
        except Exception as e:
            print(f"Rendering error: {e}")
        
        if done or truncated:
            break

    try:
        imageio.mimsave(gif_filename, frames, duration=0.1, loop=0)
    except Exception as e:
        print(f"GIF save error: {e}")
        return float(score), int(t + 1), None, steps_log

    return float(score), int(t + 1), gif_filename, steps_log


# Initialize environment once
env = setup_environment()