from stable_baselines3.a2c import A2C
from stable_baselines3.common.monitor import Monitor

from gymnasium.wrappers.time_limit import TimeLimit

from klask_environment import KlaskEnv

env = KlaskEnv(render_mode="human_unclocked")
env = TimeLimit(env, max_episode_steps=1000)
env = Monitor(env)

model = A2C("CnnPolicy", env, verbose=1).learn(total_timesteps=100_000)
