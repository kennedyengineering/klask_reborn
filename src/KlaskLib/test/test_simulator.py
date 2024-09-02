# Klask Reborn
# 2024 Braedan Kennedy (kennedyengineering)

from ..simulator.simulator import KlaskSimulator


def test_simulator_random_seed():
    """
    Determine if setting a random seed results in deterministic starting states
    """

    sim = KlaskSimulator(render_mode=None)

    iter = 15
    prev_states = []
    for _ in range(iter):
        _, _, agent_states = sim.reset(seed=10, ball_start_position="random")

        prev_states.append(tuple([*agent_states.values()]))

    assert len(set(prev_states)) == 1


def test_simulator_random_no_seed():
    """
    Determine if not setting a random seed results in random starting states
    """

    sim = KlaskSimulator(render_mode=None)

    iter = 15
    prev_states = []
    for _ in range(iter):
        _, _, agent_states = sim.reset(seed=None, ball_start_position="random")

        prev_states.append(tuple([*agent_states.values()]))

    assert len(set(prev_states)) > 1


def test_simulator_render_mode_metadata():
    """
    Determine if render_modes exists as class metadata
    """

    assert hasattr(KlaskSimulator, "render_modes")


def test_simulator_render_mode_default():
    """
    Determine if default frame rendering behaves as expected
    """

    sim = KlaskSimulator()

    assert sim.render_mode is None

    frame, _, _ = sim.reset()

    assert sim.screen is None

    assert sim.clock is None

    assert frame is None


def test_simulator_render_mode_none():
    """
    Determine if disabling frame rendering behaves as expected
    """

    sim = KlaskSimulator(render_mode=None)

    assert sim.render_mode is None

    frame, _, _ = sim.reset()

    assert sim.screen is None

    assert sim.clock is None

    assert frame is None


def test_simulator_render_mode_rgb_array():
    """
    Determine if rgb_array frame rendering behaves as expected
    """
    from numpy import ndarray

    sim = KlaskSimulator(render_mode="rgb_array")

    assert sim.render_mode == "rgb_array"

    frame, _, _ = sim.reset()

    assert sim.screen is None

    assert sim.clock is None

    assert isinstance(frame, ndarray)


def test_simulator_render_mode_human_unclocked():
    """
    Determine if human_unclocked frame rendering behaves as expected
    """
    from numpy import ndarray

    sim = KlaskSimulator(render_mode="human_unclocked")

    assert sim.render_mode == "human_unclocked"

    frame, _, _ = sim.reset()

    assert sim.screen is not None

    assert sim.clock is None

    assert isinstance(frame, ndarray)


def test_simulator_render_mode_human():
    """
    Determine if human frame rendering behaves as expected
    """
    from numpy import ndarray

    sim = KlaskSimulator(render_mode="human")

    assert sim.render_mode == "human"

    frame, _, _ = sim.reset()

    assert sim.screen is not None

    assert sim.clock is not None

    assert isinstance(frame, ndarray)


def test_simulator_ball_start_position_metadata():
    """
    Determine if ball_start_positions exists as class metadata
    """

    assert hasattr(KlaskSimulator, "ball_start_positions")
