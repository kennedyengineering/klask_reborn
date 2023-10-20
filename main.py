from dataclasses import dataclass

import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)

import Box2D
from Box2D.b2 import (world, edgeShape, vec2, pi, contactListener)

from klask_render import render_game_board
from klask_constants import *

# --- constants ---
LENGTH_SCALER = 100
PPM = 20
TARGET_FPS = 120
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = KG_BOARD_WIDTH * PPM * LENGTH_SCALER, KG_BOARD_HEIGHT * PPM * LENGTH_SCALER

# --- pygame setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Klask Simulator')
clock = pygame.time.Clock()

# --- create contact listener ---
class myContactListener(contactListener):
    def __init__(self):
        contactListener.__init__(self)
        self.collision_list = []
    def PreSolve(self, contact, oldManifold):
        bodyA = contact.fixtureA.body
        bodyB = contact.fixtureB.body
        self.collision_list.append((bodyA, bodyB))

# --- create the world ---
world = world(contactListener=myContactListener(), gravity=(0, 0), doSleep=True)

# --- static bodies ---
@dataclass
class bodyUserData:
    name: str
    color: tuple = (127, 127, 127)

wall_bottom = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0,0), (KG_BOARD_WIDTH * LENGTH_SCALER, 0)]),
    userData=bodyUserData("wall_bottom")
)
wall_left = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0,0), (0, KG_BOARD_HEIGHT * LENGTH_SCALER)]),
    userData=bodyUserData("wall_left")
)
wall_right = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(KG_BOARD_WIDTH * LENGTH_SCALER, 0), (KG_BOARD_WIDTH * LENGTH_SCALER, KG_BOARD_HEIGHT * LENGTH_SCALER)]),
    userData=bodyUserData("wall_right")
)
wall_top = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0, KG_BOARD_HEIGHT * LENGTH_SCALER), (KG_BOARD_WIDTH * LENGTH_SCALER, KG_BOARD_HEIGHT * LENGTH_SCALER)]),
    userData=bodyUserData("wall_top")
)

ground = world.CreateStaticBody(position=(0,0))

# --- dynamic bodies ---
puck1_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 2), userData=bodyUserData("puck1", KG_PUCK_COLOR))
puck1 = puck1_body.CreateCircleFixture(radius=KG_PUCK_RADIUS * LENGTH_SCALER)

puck2_body = world.CreateDynamicBody(position=(2 * KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 2), userData=bodyUserData("puck2", KG_PUCK_COLOR))
puck2 = puck2_body.CreateCircleFixture(radius=KG_PUCK_RADIUS * LENGTH_SCALER)

ball_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 3), userData=bodyUserData("ball", KG_BALL_COLOR))
ball = ball_body.CreateCircleFixture(radius=KG_BALL_RADIUS * LENGTH_SCALER, restitution=.85)

biscuit1_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, KG_BOARD_HEIGHT * LENGTH_SCALER / 2), userData=bodyUserData("biscuit1", KG_BISCUIT_COLOR))
biscuit1 = biscuit1_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7)

biscuit2_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, (KG_BOARD_HEIGHT * LENGTH_SCALER / 2) + KG_BISCUIT_START_OFFSET_Y * LENGTH_SCALER), userData=bodyUserData("biscuit2", KG_BISCUIT_COLOR))
biscuit2 = biscuit2_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7)

biscuit3_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, (KG_BOARD_HEIGHT * LENGTH_SCALER / 2) - KG_BISCUIT_START_OFFSET_Y * LENGTH_SCALER), userData=bodyUserData("biscuit3", KG_BISCUIT_COLOR))
biscuit3 = biscuit3_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7)

alive = [puck1, puck2, ball, biscuit1, biscuit2, biscuit3]

# --- create joints ---
ball_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=ball_body, maxForce=15.0)
biscuit1_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit1_body, maxForce=10.0)
biscuit2_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit2_body, maxForce=10.0)
biscuit3_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit3_body, maxForce=10.0)
puck1_mouse_joint = None

def apply_magnet_joint(bodyA, bodyB, permeability, magnetic_chargeA, magnetic_chargeB):
    # Get the distance vector between the two bodies
    force = (bodyA.position - bodyB.position)

    # Normalize the distance vector and get the Euclidean distance between the two bodies
    separation = force.Normalize()

    # Compute magnetic force between two points
    force *= (permeability * magnetic_chargeA * magnetic_chargeB) / (4 * pi * separation**2)

    # Apply forces to bodies
    bodyB.ApplyForceToCenter(force=force, wake=True)
    bodyA.ApplyForceToCenter(force=-force, wake=True)

# --- render methods ---
def draw_circle_fixture(circle, color, pixels_per_meter, surface):
    position = circle.body.transform * circle.shape.pos * pixels_per_meter
    position = (position[0], surface.get_height() - position[1])
    pygame.draw.circle(screen, color, [int(x) for x in position], int(circle.shape.radius * pixels_per_meter))

# --- main game loop ---
game_board = render_game_board(PPM * LENGTH_SCALER)

running = True
while running:
    # Check the event queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # The user closed the window or pressed escape
            running = False

        # Control Puck 1
        if event.type == MOUSEBUTTONDOWN:
            if puck1_mouse_joint:
                world.DestroyJoint(puck1_mouse_joint)
            puck1_mouse_joint = world.CreateMouseJoint(bodyA=ground, bodyB=puck1_body, target=puck1_body.position, maxForce=10000)#, dampingRatio=1.0, frequencyHz=60)
        elif event.type == MOUSEBUTTONUP:
            if puck1_mouse_joint:
                world.DestroyJoint(puck1_mouse_joint)
            puck1_mouse_joint = None
            puck1_body.linearVelocity = (0, 0)
        elif event.type == MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            if puck1_mouse_joint:
                puck1_mouse_joint.target = (x / PPM, (SCREEN_HEIGHT - y) / PPM)

    # Control Puck 2
    puck2_body.linearVelocity = vec2(0, 0)

    # Apply Magnetic Force
    permeability_air = 1.25663753e10-6  
    magnetic_charge = 0.001
    force = (puck1_body.position - biscuit1_body.position)
    distance = force.Normalize()
    force *= (permeability_air * magnetic_charge**2) / (4 * pi * distance**2)
    biscuit1_body.ApplyForceToCenter(force=force, wake=True)

    # Render the world
    screen.blit(game_board, (0,0))

    # Draw the world
    for fixture in alive:
        draw_circle_fixture(fixture, fixture.body.userData.color, PPM, screen)

    # Control Puck 1
    # keys = pygame.key.get_pressed()
    # force = 100000
    # # puck1_body.linearVelocity= vec2(0,0)
    # if keys[K_w]:
    #     # puck1_body.ApplyForceToCenter(vec2(0, force), wake=True)
    #     puck1_body.ApplyLinearImpulse(vec2(0, force), puck1_body.position, wake=True)
    # if keys[K_s]:
    #     #  puck1_body.ApplyForceToCenter(vec2(0, -force), wake=True)
    #     puck1_body.ApplyLinearImpulse(vec2(0, -force), puck1_body.position, wake=True)
    # if keys[K_a]:
    #     #  puck1_body.ApplyForceToCenter(vec2(-force, 0), wake=True)
    #     puck1_body.ApplyLinearImpulse(vec2(-force, 0), puck1_body.position, wake=True)
    # if keys[K_d]:
    #     # puck1_body.ApplyForceToCenter(vec2(force, 0), wake=True)
    #     puck1_body.ApplyLinearImpulse(vec2(force, 0), puck1_body.position, wake=True)

    # Make Box2D simulate the physics of our world for one step.
    world.Step(TIME_STEP, 10, 10)

    # Handle collisions
    while world.contactListener.collision_list:
        # Sort body by name
        bodyA, bodyB = world.contactListener.collision_list.pop()
        names = {bodyA.userData.name : bodyA, bodyB.userData.name : bodyB}
        
        if "puck1" in names and "biscuit1" in names:
            print("biscuit!")
            # world.DestroyBody(biscuit1_body)

    # Flip the screen and try to keep at the target FPS
    pygame.display.flip()
    clock.tick(TARGET_FPS)
    # print(clock.get_fps())

pygame.quit()
