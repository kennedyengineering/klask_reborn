import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)

import Box2D
from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)

from klask_render import render_game_board
from klask_constants import *

# --- constants ---
# Box2D deals with meters, but we want to display pixels,
# so define a conversion factor:
# PPM = 20.0  # pixels per meter
PPM = 2000
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = KG_BOARD_WIDTH * PPM, KG_BOARD_HEIGHT * PPM

# --- pygame setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Simple pygame example')
clock = pygame.time.Clock()

# --- pybox2d world setup ---
# Create the world
world = world(gravity=(0, -9.8), doSleep=True)

# --- static bodies ---
wall_bottom = world.CreateStaticBody(
    position=(0, 0),
    shapes=polygonShape(box=(KG_BOARD_WIDTH, 0))
)
wall_left = world.CreateStaticBody(
    position=(0, 0),
    shapes=polygonShape(box=(0, KG_BOARD_HEIGHT))
)
wall_right = world.CreateStaticBody(
    position=(KG_BOARD_WIDTH, 0),
    shapes=polygonShape(box=(0, KG_BOARD_HEIGHT))
)
wall_top = world.CreateStaticBody(
    position=(0, KG_BOARD_HEIGHT),
    shapes=polygonShape(box=(KG_BOARD_WIDTH, 0))
)

ground = world.CreateStaticBody(position=(0,0))
ground_fixture = ground.CreatePolygonFixture(box=(KG_BOARD_WIDTH, KG_BOARD_HEIGHT), density=1, friction=0.3)

# --- dynamic bodies ---

ball_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH / 2, KG_BOARD_HEIGHT / 2))
ball = ball_body.CreateCircleFixture(radius=KG_BALL_RADIUS, density=1, friction=0.3)

# Create joint
joint = world.CreateFrictionJoint(bodyA=ground, bodyB=ball_body, maxForce=0.0015)

colors = {
    staticBody: (255, 255, 255, 255),
    dynamicBody: (127, 127, 127, 255),
}

def my_draw_polygon(polygon, body, fixture):
    # vertices = [(body.transform * v) * PPM for v in polygon.vertices]
    # vertices = [(v[0], SCREEN_HEIGHT - v[1]) for v in vertices]
    # pygame.draw.polygon(screen, colors[body.type], vertices)
    pass
polygonShape.draw = my_draw_polygon

def my_draw_circle(circle, body, fixture):
    position = body.transform * circle.pos * PPM
    position = (position[0], SCREEN_HEIGHT - position[1])
    pygame.draw.circle(screen, colors[body.type], [int(
        x) for x in position], int(circle.radius * PPM))
circleShape.draw = my_draw_circle

# --- main game loop ---

game_board = render_game_board(PPM)

running = True
while running:
    # Check the event queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # The user closed the window or pressed escape
            running = False

    screen.blit(game_board, (0,0))

    # Draw the world
    for body in world.bodies:
        for fixture in body.fixtures:
            fixture.shape.draw(body, fixture)

    # Make Box2D simulate the physics of our world for one step.
    world.Step(TIME_STEP, 10, 10)

    # Flip the screen and try to keep at the target FPS
    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()
print('Done!')

