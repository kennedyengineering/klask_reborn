from stable_baselines3.common.env_checker import check_env
from ..environment.environment import KlaskEnv


def test_sb3_env_checker():
    env = KlaskEnv()
    check_env(env)
