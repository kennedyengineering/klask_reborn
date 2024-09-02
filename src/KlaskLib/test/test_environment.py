# Klask Reborn
# 2024 Braedan Kennedy (kennedyengineering)

from ..environment.environment import KlaskEnv

from stable_baselines3.common.env_checker import check_env as sb3_check_env
from gymnasium.utils.env_checker import check_env as gym_check_env


def test_sb3_env_checker():
    env = KlaskEnv()
    sb3_check_env(env)


def test_gym_env_checker():
    env = KlaskEnv()
    gym_check_env(env)
