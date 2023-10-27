from klask_simulator import KlaskSimulator

import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)

# initialize the simulator
sim = KlaskSimulator(render_mode="human")

sim.reset()

running = True

while running:
    # Check the event queue (only accessable if render_mode="human")
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # The user closed the window or pressed escape
            running = False

    sim.step((0,0.0001), (0,0))

sim.close()
