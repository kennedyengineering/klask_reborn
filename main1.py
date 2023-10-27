from klask_simulator import KlaskSimulator

sim = KlaskSimulator(render_mode="")

sim.reset()

sim.step((0.02,0.00), (0.03,0))

while 1:
    sim.step((0,0.0001), (0,0))