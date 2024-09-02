# Klask Reborn
# 2024 Braedan Kennedy (kennedyengineering)

from stable_baselines3.a2c import A2C
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor

from gymnasium.wrappers.time_limit import TimeLimit

from KlaskLib.environment.environment import KlaskEnv
from ParseLib.sanitization.filesystem import check_directory
from ParseLib.sanitization.number import check_positive_int

import argparse
import datetime
import os


def make_env(render_mode=None, time_limit=None):
    def _init():

        env = KlaskEnv(render_mode=render_mode)

        if time_limit:
            env = TimeLimit(env, max_episode_steps=time_limit)

        return env

    return _init


def main():
    # Configure argument parser
    parser = argparse.ArgumentParser()
    # Filesystem and logging parameters
    parser.add_argument("--runs-directory", type=check_directory, default="runs/")
    parser.add_argument("--weights-directory", type=check_directory, default="weights/")
    # Environment parameters
    parser.add_argument("--envs", type=check_positive_int, default=5)
    parser.add_argument(
        "--render-mode",
        type=str,
        choices=KlaskEnv.metadata["render_modes"],
        default="rgb_array",
    )
    parser.add_argument("--time-limit", type=check_positive_int, default=1000)
    # Training parameters
    parser.add_argument("--timesteps", type=check_positive_int, default=100_000)
    parser.add_argument("--verbose", type=int, choices=range(3), default=1)
    # Parse arguments
    args = parser.parse_args()

    # Initialize runtime variables
    start_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    log_path = os.path.join(args.runs_directory, "run_%s" % start_time)
    weight_path = os.path.join(args.weights_directory, "weight_%s" % start_time)

    # Display starting message
    print("Starting Training @ %s" % (start_time))
    print()
    print("Configuration:")
    for arg in vars(args):
        print("\t", arg, ":", getattr(args, arg))
    print()

    # Create environment
    vec_env = SubprocVecEnv(
        [
            make_env(render_mode=args.render_mode, time_limit=args.time_limit)
            for _ in range(args.envs)
        ]
    )
    vec_env = VecMonitor(vec_env)

    # Create model
    model = A2C("CnnPolicy", vec_env, verbose=args.verbose, tensorboard_log=log_path)

    # Train model
    model.learn(total_timesteps=args.timesteps)

    # Save model
    model.save(weight_path)


if __name__ == "__main__":
    main()
