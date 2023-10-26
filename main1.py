from klask_simulator import KlaskSimulator

sim = KlaskSimulator()

sim.reset()

while 1:
    sim.step((0,1.01), (0,-1.01))