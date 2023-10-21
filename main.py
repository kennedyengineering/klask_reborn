from dataclasses import dataclass

import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)

import Box2D
from Box2D.b2 import (world, edgeShape, vec2, pi, contactListener)

from klask_render import render_game_board
from klask_constants import *


# TODO: can use the number of fixtures on puck* to count the number of biscuits attached
# TODO: fix ball getting stuck along walls


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
    def PostSolve(self, contact, oldManifold):
        self.collision_list.append((contact.fixtureA, contact.fixtureB))

# --- create the world ---
world = world(contactListener=myContactListener(), gravity=(0, 0), doSleep=True)

# --- static bodies ---
wall_bottom = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0,0), (KG_BOARD_WIDTH * LENGTH_SCALER, 0)])
)
wall_left = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0,0), (0, KG_BOARD_HEIGHT * LENGTH_SCALER)])
)
wall_right = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(KG_BOARD_WIDTH * LENGTH_SCALER, 0), (KG_BOARD_WIDTH * LENGTH_SCALER, KG_BOARD_HEIGHT * LENGTH_SCALER)])
)
wall_top = world.CreateStaticBody(
    position=(0, 0),
    shapes=edgeShape(vertices=[(0, KG_BOARD_HEIGHT * LENGTH_SCALER), (KG_BOARD_WIDTH * LENGTH_SCALER, KG_BOARD_HEIGHT * LENGTH_SCALER)])
)

ground = world.CreateStaticBody(position=(0,0))
@dataclass
class fixtureUserData:
    name: str
    color: tuple

# --- dynamic bodies ---
puck1_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 2))
puck1 = puck1_body.CreateCircleFixture(radius=KG_PUCK_RADIUS * LENGTH_SCALER, userData=fixtureUserData("puck1", KG_PUCK_COLOR))

puck2_body = world.CreateDynamicBody(position=(2 * KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 2))
puck2 = puck2_body.CreateCircleFixture(radius=KG_PUCK_RADIUS * LENGTH_SCALER, userData=fixtureUserData("puck2", KG_PUCK_COLOR))

ball_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 3))
ball = ball_body.CreateCircleFixture(radius=KG_BALL_RADIUS * LENGTH_SCALER, restitution=.85, userData=fixtureUserData("ball", KG_BALL_COLOR))

biscuit1_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, KG_BOARD_HEIGHT * LENGTH_SCALER / 2))
biscuit1 = biscuit1_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7, userData=fixtureUserData("biscuit1", KG_BISCUIT_COLOR))

biscuit2_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, (KG_BOARD_HEIGHT * LENGTH_SCALER / 2) + KG_BISCUIT_START_OFFSET_Y * LENGTH_SCALER))
biscuit2 = biscuit2_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7, userData=fixtureUserData("biscuit2", KG_BISCUIT_COLOR))

biscuit3_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, (KG_BOARD_HEIGHT * LENGTH_SCALER / 2) - KG_BISCUIT_START_OFFSET_Y * LENGTH_SCALER))
biscuit3 = biscuit3_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7, userData=fixtureUserData("biscuit3", KG_BISCUIT_COLOR))

biscuit_bodies = [biscuit1_body, biscuit2_body, biscuit3_body]
render_bodies = [puck1_body, puck2_body, ball_body, biscuit1_body, biscuit2_body, biscuit3_body]

# --- create joints ---
ball_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=ball_body, maxForce=15.0)
biscuit1_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit1_body, maxForce=10.0)
biscuit2_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit2_body, maxForce=10.0)
biscuit3_ground_joint = world.CreateFrictionJoint(bodyA=ground, bodyB=biscuit3_body, maxForce=10.0)
puck1_mouse_joint = None

def apply_magnet_force(puck_body, biscuit_body, permeability, magnetic_charge):
    # Get the distance vector between the two bodies
    force = (puck_body.position - biscuit_body.position)

    # Normalize the distance vector and get the Euclidean distance between the two bodies
    separation = force.Normalize()

    # Compute magnetic force between two points
    force *= (permeability * magnetic_charge**2) / (4 * pi * separation**2)

    # Apply forces to bodies
    biscuit_body.ApplyForceToCenter(force=force, wake=True)

# --- render methods ---
def draw_circle_fixture(circle, pixels_per_meter, surface):
    position = circle.body.transform * circle.shape.pos * pixels_per_meter
    position = (position[0], surface.get_height() - position[1])
    pygame.draw.circle(screen, circle.userData.color, [int(x) for x in position], int(circle.shape.radius * pixels_per_meter))

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
    for biscuit_body in biscuit_bodies:
        apply_magnet_force(puck1_body, biscuit_body, KG_PERMEABILITY_AIR, KG_MAGNETIC_CHARGE)
        apply_magnet_force(puck2_body, biscuit_body, KG_PERMEABILITY_AIR, KG_MAGNETIC_CHARGE)

    # Render the world
    screen.blit(game_board, (0,0))

    # Draw the world
    for body in render_bodies:
        for fixture in body:
            draw_circle_fixture(fixture, PPM, screen)

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
        fixtureA, fixtureB = world.contactListener.collision_list.pop()
        
        # Check if a collision with a static body
        if fixtureA.userData is None or fixtureB.userData is None:
            continue

        names = {fixtureA.userData.name : fixtureA, fixtureB.userData.name : fixtureB}
        keys = list(names.keys())

        # Determine if collision between puck and biscuit
        if any(["puck" in x for x in keys]) and any(["biscuit" in x for x in keys]):
            puck = names[min(keys, key=len)]
            biscuit = names[max(keys, key=len)]
            
            position = (biscuit.body.position - puck.body.position)
            position.Normalize()
            position = position * (puck.shape.radius + biscuit.shape.radius / 2)

            new_biscuit = puck.body.CreateCircleFixture(radius=biscuit.shape.radius, pos=position, userData=biscuit.userData)
            new_biscuit.sensor = True

            biscuit_bodies.remove(biscuit.body)
            render_bodies.remove(biscuit.body)
            world.DestroyBody(biscuit.body)

    # Flip the screen and try to keep at the target FPS
    pygame.display.flip()
    clock.tick(TARGET_FPS)
    # print(clock.get_fps())

pygame.quit()
