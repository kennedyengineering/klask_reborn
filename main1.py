from klask_simulator import KlaskSimulator

sim = KlaskSimulator()

sim.reset()

sim.step((0.01,0), (0,0))

while 1:
    sim.step((0,0), (0,0))