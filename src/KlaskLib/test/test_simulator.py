from ..simulator.simulator import KlaskSimulator


def test_simulator_random_seed():
    """
    Determine if setting a random seed results in deterministic starting states
    """

    # TODO: change render_mode to None (should be default at some point)
    sim = KlaskSimulator(render_mode="headless")

    seed = 10
    iter = 15
    prev_states = []
    for _ in range(iter):
        frame, game_states, agent_states = sim.reset(
            seed=10, ball_start_position="random"
        )

        prev_states.append(agent_states)

    assert len(set(prev_states)) == 1


def test_simulator_random_no_seed():
    """
    Determine if not setting a random seed results in random starting states
    """

    # TODO: change render_mode to None (should be default at some point)
    sim = KlaskSimulator(render_mode="headless")

    iter = 15
    prev_states = []
    for _ in range(iter):
        frame, game_states, agent_states = sim.reset(
            seed=None, ball_start_position="random"
        )

        prev_states.append(agent_states)

    assert len(set(prev_states)) > 1
