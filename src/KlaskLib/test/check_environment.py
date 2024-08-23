from stable_baselines3.common.env_checker import check_env
from klask_environment import KlaskEnv

env = KlaskEnv()

check_env(env)
