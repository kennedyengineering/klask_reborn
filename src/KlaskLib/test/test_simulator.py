from ..simulator.simulator import KlaskSimulator


def test_simulator_random_seed():
    """
    Determine if setting a random seed results in deterministic starting states
    """

    sim = KlaskSimulator(render_mode=None)

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

    sim = KlaskSimulator(render_mode=None)

    iter = 15
    prev_states = []
    for _ in range(iter):
        frame, game_states, agent_states = sim.reset(
            seed=None, ball_start_position="random"
        )

        prev_states.append(agent_states)

    assert len(set(prev_states)) > 1
