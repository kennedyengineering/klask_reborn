from stable_baselines3.a2c import A2C
from stable_baselines3.common.monitor import Monitor

from klask_environment import KlaskEnv

env = Monitor(KlaskEnv())

model = A2C("CnnPolicy", env, verbose=1).learn(total_timesteps=10_000)
