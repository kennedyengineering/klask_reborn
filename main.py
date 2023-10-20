import pygame
from pygame.locals import (QUIT, KEYDOWN, KEYUP, K_ESCAPE, K_w, K_a, K_s, K_d)

import Box2D
from Box2D.b2 import (world, edgeShape, polygonShape, circleShape, staticBody, dynamicBody, kinematicBody, vec2)

from klask_render import render_game_board
from klask_constants import *

# TODO: scale up sizes for more accurate simulation

# --- constants ---
# Box2D deals with meters, but we want to display pixels,
# so define a conversion factor:
PPM = 2000
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = KG_BOARD_WIDTH * PPM, KG_BOARD_HEIGHT * PPM

# --- pygame setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Klask Simulator')
clock = pygame.time.Clock()

# --- pybox2d world setup ---
# Create the world
world = world(gravity=(0, 0), doSleep=True)

# --- static bodies ---
wall_bottom = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0,0), (KG_BOARD_WIDTH, 0)])
)
wall_left = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0,0), (0, KG_BOARD_HEIGHT)])
)
wall_right = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(KG_BOARD_WIDTH, 0), (KG_BOARD_WIDTH, KG_BOARD_HEIGHT)])
)
wall_top = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0, KG_BOARD_HEIGHT), (KG_BOARD_WIDTH, KG_BOARD_HEIGHT)])
)

ground = world.CreateStaticBody(position=(0,0))
ground_fixture = ground.CreatePolygonFixture(box=(KG_BOARD_WIDTH, KG_BOARD_HEIGHT), density=1, friction=0.3)

# --- dynamic bodies ---
puck1_body = world.CreateDynamicBody(
    position=(KG_BOARD_WIDTH / 3, KG_BOARD_HEIGHT / 2), 
    shapes=circleShape(radius=KG_BALL_RADIUS),
    bullet=True
)

puck2_body = world.CreateDynamicBody(
    position=(2 * (KG_BOARD_WIDTH / 3), KG_BOARD_HEIGHT / 2), 
    shapes=circleShape(radius=KG_BALL_RADIUS)
)

ball_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH / 3, KG_BOARD_HEIGHT / 3))
ball = ball_body.CreateCircleFixture(radius=KG_BALL_RADIUS, density=1, friction=0.3)

biscuit1_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH / 2, KG_BOARD_HEIGHT / 2))
biscuit1 = biscuit1_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS, density=1, friction=0.3)

biscuit2_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH / 2, (KG_BOARD_HEIGHT / 2) + KG_BISCUIT_START_OFFSET_Y))
biscuit2 = biscuit2_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS, density=1, friction=0.3)

biscuit3_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH / 2, (KG_BOARD_HEIGHT / 2) - KG_BISCUIT_START_OFFSET_Y))
biscuit3 = biscuit3_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS, density=1, friction=0.3)

# --- create joints ---
ball_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=ball_body, maxForce=0.0015)
biscuit1_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit1_body, maxForce=0.0015)
biscuit2_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit2_body, maxForce=0.0015)
biscuit3_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit3_body, maxForce=0.0015)
puck1_body_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=puck1_body, maxForce=0.0)
puck2_body_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=puck2_body, maxForce=0.0)

def draw_circle_fixture(circle, color, pixels_per_meter, surface):
    position = circle.body.transform * circle.shape.pos * pixels_per_meter
    position = (position[0], surface.get_height() - position[1])
    pygame.draw.circle(screen, color, [int(x) for x in position], int(circle.shape.radius * pixels_per_meter))

# --- main game loop ---
game_board = render_game_board(PPM)

running = True
while running:
    # Check the event queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # The user closed the window or pressed escape
            running = False
        elif event.type == KEYDOWN:
            if event.key==K_w:
                puck1_body.linearVelocity = vec2(0, 0.1)
            if event.key==K_s:
                puck1_body.linearVelocity = vec2(0, -0.1)
            if event.key==K_a:
                puck1_body.linearVelocity = vec2(-0.1 ,0)
            if event.key==K_d:
                puck1_body.linearVelocity = vec2(0.1, 0)
        elif event.type == KEYUP:
            puck1_body.linearVelocity = vec2(0, 0)
    

    # Render the world
    screen.blit(game_board, (0,0))

    # Draw the world

    draw_circle_fixture(puck1_body.fixtures[0], KG_PUCK_COLOR, PPM, screen)
    draw_circle_fixture(puck2_body.fixtures[0], KG_PUCK_COLOR, PPM, screen)
    draw_circle_fixture(ball, KG_BALL_COLOR, PPM, screen)
    draw_circle_fixture(biscuit1, KG_BISCUIT_COLOR, PPM, screen)
    draw_circle_fixture(biscuit2, KG_BISCUIT_COLOR, PPM, screen)
    draw_circle_fixture(biscuit3, KG_BISCUIT_COLOR, PPM, screen)


    # Apply forces
    # ball_body.ApplyForce(force=(0.0005, 0), point=ball.shape.pos, wake=True)
    # biscuit1_body.ApplyForce(force=(0.0015, 0), point=biscuit1.shape.pos, wake=True)
    # biscuit2_body.ApplyForce(force=(0.0015, 0), point=biscuit2.shape.pos, wake=True)
    # biscuit3_body.ApplyForce(force=(0.0015, 0), point=biscuit3.shape.pos, wake=True)

    # Make Box2D simulate the physics of our world for one step.
    world.Step(TIME_STEP, 10, 10)
    world.ClearForces()

    # Flip the screen and try to keep at the target FPS
    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()
print('Done!')

