# Klask Reborn
# 2024 Braedan Kennedy (kennedyengineering)

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from ..simulator.simulator import KlaskSimulator

# TODO: Verify biscuit never has a negative position, or position greater than the width of the board
# TODO: zero-pad output frame to make dimensions even
# TODO: make render_fps in metadata do something (connect to display_fps)
# TODO: either use or remove options argument (maybe have it contain ball_start_position, or render options?)
# TODO: allow for None type render mode, change output type?
# TODO: add option for rich & simple render mode (simple: no logo or extra lines)
# TODO: normalize MLP agent_states [0-1]
# TODO: get anti-aliased rendering from PyGame
# TODO: make reward function its own method, seperate file (takes game_states and agent_states as input)
# TODO: add self-play somehow

# TODO: move the constants file, or make env parameter
MAX_FORCE = 0.015


class KlaskEnv(gym.Env):
    # TODO: redo banner
    """Custom environment that follows Gymnasium interface."""

    metadata = {
        "render_modes": ["human", "human_unclocked", "rgb_array"],
        "render_fps": 120,
    }

    def __init__(self, render_mode="rgb_array"):
        super().__init__()

        # Initialize simulator
        assert render_mode in self.metadata["render_modes"], "Invalid render mode"
        self.sim = KlaskSimulator(render_mode=render_mode)

        # Using continuous actions
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0]), high=np.array([1.0, 1.0]), dtype=np.float32
        )

        # Using image as input (channel-first; channel-last also works)
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(3, 609, 787), dtype=np.uint8
        )

    def step(self, action):
        # Apply the action to the environment
        assert self.action_space.contains(action), "Invalid action"
        frame, game_states, agent_states = self.sim.step(
            (action[0] * MAX_FORCE, action[1] * MAX_FORCE), (0.0, 0.0)
        )

        # Process observation
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

        # FIXME: check if this is correct
        # Check if episode is done
        terminated = truncated = not KlaskSimulator.GameStates.PLAYING in game_states

        # TODO: utilize info dict
        # Return
        info = {}
        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Reset simulator
        frame, game_states, agent_states = self.sim.reset(seed=seed)

        # Process observation
        observation = np.moveaxis(frame, -1, 0)

        # TODO: utilize info dict
        # Return
        info = {}
        return observation, info
