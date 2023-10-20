import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)

import Box2D
from Box2D.b2 import (world, edgeShape, vec2, pi, contactListener, getPointStates, addState)

from klask_render import render_game_board
from klask_constants import *

# --- constants ---
# Box2D deals with meters, but we want to display pixels,
# so define a conversion factor:
LENGTH_SCALER = 100
PPM = 20
TARGET_FPS = 120
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = KG_BOARD_WIDTH * PPM * LENGTH_SCALER, KG_BOARD_HEIGHT * PPM * LENGTH_SCALER

# --- pygame setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Klask Simulator')
clock = pygame.time.Clock()

# --- pybox2d world setup ---
# --- create contact listener ---
class myContactListener(contactListener):
    def __init__(self):
        contactListener.__init__(self)
    def BeginContact(self, contact):
        pass
    def EndContact(self, contact):
        pass
    def PreSolve(self, contact, oldManifold):
        bodyA = contact.fixtureA.body
        bodyB = contact.fixtureB.body
        print(contact)
    def PostSolve(self, contact, impulse):
        pass

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

# --- dynamic bodies ---
puck1_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 2))
puck1 = puck1_body.CreateCircleFixture(radius=KG_PUCK_RADIUS * LENGTH_SCALER)

puck2_body = world.CreateDynamicBody(position=(2 * KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 2))
puck2 = puck2_body.CreateCircleFixture(radius=KG_PUCK_RADIUS * LENGTH_SCALER)

ball_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 3, KG_BOARD_HEIGHT * LENGTH_SCALER / 3))
ball = ball_body.CreateCircleFixture(radius=KG_BALL_RADIUS * LENGTH_SCALER, restitution=.85)

biscuit1_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, KG_BOARD_HEIGHT * LENGTH_SCALER / 2))
biscuit1 = biscuit1_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7)

biscuit2_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, (KG_BOARD_HEIGHT * LENGTH_SCALER / 2) + KG_BISCUIT_START_OFFSET_Y * LENGTH_SCALER))
biscuit2 = biscuit2_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7)

biscuit3_body = world.CreateDynamicBody(position=(KG_BOARD_WIDTH * LENGTH_SCALER / 2, (KG_BOARD_HEIGHT * LENGTH_SCALER / 2) - KG_BISCUIT_START_OFFSET_Y * LENGTH_SCALER))
biscuit3 = biscuit3_body.CreateCircleFixture(radius=KG_BISCUIT_RADIUS * LENGTH_SCALER, restitution=.7)

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
    draw_circle_fixture(puck1, KG_PUCK_COLOR, PPM, screen)
    draw_circle_fixture(puck2, KG_PUCK_COLOR, PPM, screen)
    draw_circle_fixture(ball, KG_BALL_COLOR, PPM, screen)
    draw_circle_fixture(biscuit1, KG_BISCUIT_COLOR, PPM, screen)
    draw_circle_fixture(biscuit2, KG_BISCUIT_COLOR, PPM, screen)
    draw_circle_fixture(biscuit3, KG_BISCUIT_COLOR, PPM, screen)

    # Apply forces
    # ball_body.ApplyForce(force=(0.0005, 0), point=ball.shape.pos, wake=True)
    # biscuit1_body.ApplyForce(force=(0.0015, 0), point=biscuit1.shape.pos, wake=True)
    # biscuit2_body.ApplyForce(force=(0.0015, 0), point=biscuit2.shape.pos, wake=True)
    # biscuit3_body.ApplyForce(force=(0.0015, 0), point=biscuit3.shape.pos, wake=True)

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

    # Flip the screen and try to keep at the target FPS
    pygame.display.flip()
    clock.tick(TARGET_FPS)
    # print(clock.get_fps())

pygame.quit()
print('Done!')

