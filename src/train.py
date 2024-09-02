from stable_baselines3.a2c import A2C
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor

from gymnasium.wrappers.time_limit import TimeLimit

from KlaskLib.environment.environment import KlaskEnv


def make_env():
    def _init():

        env = KlaskEnv(render_mode="human_unclocked")
        env = TimeLimit(env, max_episode_steps=1000)

        return env

    return _init


def main():
    vec_env = SubprocVecEnv([make_env() for _ in range(5)])
    vec_env = VecMonitor(vec_env)

    model = A2C("CnnPolicy", vec_env, verbose=1).learn(total_timesteps=100_000)


if __name__ == "__main__":
    main()
