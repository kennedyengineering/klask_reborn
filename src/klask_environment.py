import gymnasium as gym
import numpy as np
import random
from gymnasium import spaces

from klask_simulator import KlaskSimulator


MAX_FORCE = 0.015


class KlaskEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render_modes": ["human", "human_unclocked", "frame"], "render_fps": 30}

    def __init__(self, render_mode="frame"):
        super().__init__()

        # Using continuous actions:
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0]), high=np.array([1.0, 1.0]), dtype=np.float32
        )

        # Using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(3, 609, 787), dtype=np.uint8
        )

        assert render_mode in self.metadata["render_modes"]
        self.sim = KlaskSimulator(render_mode=render_mode)

    def step(self, action):
        # Apply the action to the environment
        assert self.action_space.contains(action), "Invalid action"
        frame, game_states, agent_states = self.sim.step(
            (action[0] * MAX_FORCE, action[1] * MAX_FORCE), (0.0, 0.0)
        )
        observation = np.moveaxis(frame, -1, 0)

        # Compute the reward
        reward = 0.0
        if KlaskSimulator.GameStates.P1_WIN in game_states:
            # Reward for winning
            reward += 1000.0
        if KlaskSimulator.GameStates.P2_WIN in game_states:
            # Reward for losing
            reward -= 1000.0
        if KlaskSimulator.GameStates.PLAYING in game_states:
            # Reward for staying alive
            reward += 0.1

        # Check if episode is done
        terminated = truncated = not KlaskSimulator.GameStates.PLAYING in game_states

        # Return
        info = {}
        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        # Set random seed used in simulator
        if seed:
            random.seed(seed)

        # Reset simulator
        frame, game_states, agent_states = self.sim.reset()
        observation = np.moveaxis(frame, -1, 0)

        info = {}
        return observation, info

    def render(self):
        pass

    def close(self):
        pass
