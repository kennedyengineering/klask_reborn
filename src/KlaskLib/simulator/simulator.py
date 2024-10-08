# Klask Reborn
# 2024 Braedan Kennedy (kennedyengineering)

from Box2D.b2 import contactListener, world, edgeShape, pi
from .constants import *
from dataclasses import dataclass
from enum import unique, Enum
from math import dist
from PIL import Image
from contextlib import redirect_stdout

import random


class KlaskSimulator:
    @dataclass
    class FixtureUserData:
        name: str
        color: tuple

    @unique
    class GameStates(Enum):
        PLAYING = 0  # Default state
        P1_WIN = 1  # Player 1 wins point, terminal state
        P1_SCORE = 2  # Player 1 scores goal, results in P1_WIN
        P1_KLASK = 3  # Player 1 enters own goal, results in P2_WIN
        P1_TWO_BISCUIT = 4  # Player 1 has contacted two biscuits, results in P2_WIN
        P2_WIN = 5  # Player 2 wins point, terminal state
        P2_SCORE = 6  # Player 2 scores goal, results in P2_WIN
        P2_KLASK = 7  # Player 2 enters own goal, results in P1_WIN
        P2_TWO_BISCUIT = 8  # Player 2 has contacted two biscuits, results in P1_WIN

    class KlaskContactListener(contactListener):
        def __init__(self):
            contactListener.__init__(self)

            # List of puck to biscuit collisions
            self.collision_list = []

        def PreSolve(self, contact, oldManifold):
            # Change the characteristics of the contact before the collision response is calculated

            # Check if a collision with a static body
            if contact.fixtureA.userData is None or contact.fixtureB.userData is None:
                return

            names = {
                contact.fixtureA.userData.name: contact.fixtureA,
                contact.fixtureB.userData.name: contact.fixtureB,
            }
            keys = list(names.keys())

            # Determine if collision is between puck and biscuit
            if any(["puck" in x for x in keys]) and any(["biscuit" in x for x in keys]):

                # Retrieve fixtures
                puck = names[min(keys, key=len)]
                biscuit = names[max(keys, key=len)]

                # Disable contact
                contact.enabled = False

                # Mark biscuit for deletion
                self.collision_list.append((puck, biscuit))

    ball_start_positions = [
        "top_right",  # Place the ball in the top right corner at game start
        "bottom_right",  # Place the ball in the bottom right corner at game start
        "top_left",  # Place the ball in the top left corner at game start
        "bottom_left",  # Place the ball in the bottom left corner at game start
        "random",  # Place the ball in a random corner at game start
    ]

    render_modes = [
        "human",  # "human" shows the rendered frame at the specified frame rate.
        "human_unclocked",  # "human_unclocked" shows the rendered frame at an unbounded frame rate.
        "rgb_array",  # "rgb_array" renders the frame, but does not show it.
        None,  # (default) does not render or display frame.
    ]

    def __init__(
        self,
        render_mode=None,
        length_scaler=100,
        pixels_per_meter=20,
        display_fps=120,
        simulation_fps=120,
        velocity_iterations=10,
        position_iterations=10,
    ):
        # Store user parameters
        assert render_mode in self.render_modes
        self.render_mode = render_mode

        self.length_scaler = length_scaler  # Box2D doesn't simulate small objects well. Scale klask_constants length values into the meter range.
        self.pixels_per_meter = pixels_per_meter  # Box2D uses 1 pixel / 1 meter by default. Change for better viewing.
        self.display_fps = display_fps
        self.velocity_iterations = velocity_iterations
        self.position_iterations = position_iterations

        # Compute additional parameters
        self.time_step = 1.0 / simulation_fps
        self.screen_width = KG_BOARD_WIDTH * self.pixels_per_meter * self.length_scaler
        self.screen_height = (
            KG_BOARD_HEIGHT * self.pixels_per_meter * self.length_scaler
        )

        # Internal state variables
        self.is_initialized = False

        # PyGame variables
        self.screen = None
        self.clock = None
        self.game_board = None

        # Box2D variables
        self.world = None
        self.bodies = None
        self.magnet_bodies = None
        self.render_bodies = None

    def reset(self, seed=None, ball_start_position="random"):
        # Validate ball start position
        assert ball_start_position in self.ball_start_positions

        # Set random seed
        if seed:
            random.seed(seed)

        # Create world
        self.world = world(
            contactListener=self.KlaskContactListener(), gravity=(0, 0), doSleep=True
        )

        # Create static bodies
        self.bodies = {}

        self.bodies["wall_bottom"] = self.world.CreateStaticBody(
            position=(0, 0),
            shapes=edgeShape(
                vertices=[(0, 0), (KG_BOARD_WIDTH * self.length_scaler, 0)]
            ),
        )
        self.bodies["wall_left"] = self.world.CreateStaticBody(
            position=(0, 0),
            shapes=edgeShape(
                vertices=[(0, 0), (0, KG_BOARD_HEIGHT * self.length_scaler)]
            ),
        )
        self.bodies["wall_right"] = self.world.CreateStaticBody(
            position=(0, 0),
            shapes=edgeShape(
                vertices=[
                    (KG_BOARD_WIDTH * self.length_scaler, 0),
                    (
                        KG_BOARD_WIDTH * self.length_scaler,
                        KG_BOARD_HEIGHT * self.length_scaler,
                    ),
                ]
            ),
        )
        self.bodies["wall_top"] = self.world.CreateStaticBody(
            position=(0, 0),
            shapes=edgeShape(
                vertices=[
                    (0, KG_BOARD_HEIGHT * self.length_scaler),
                    (
                        KG_BOARD_WIDTH * self.length_scaler,
                        KG_BOARD_HEIGHT * self.length_scaler,
                    ),
                ]
            ),
        )
        self.bodies["divider_left"] = self.world.CreateStaticBody(
            position=(0, 0),
            shapes=edgeShape(
                vertices=[
                    (
                        KG_BOARD_WIDTH * self.length_scaler / 2
                        - KG_DIVIDER_WIDTH * self.length_scaler / 2,
                        0,
                    ),
                    (
                        KG_BOARD_WIDTH * self.length_scaler / 2
                        - KG_DIVIDER_WIDTH * self.length_scaler / 2,
                        KG_BOARD_HEIGHT * self.length_scaler,
                    ),
                ]
            ),
        )
        self.bodies["divider_right"] = self.world.CreateStaticBody(
            position=(0, 0),
            shapes=edgeShape(
                vertices=[
                    (
                        KG_BOARD_WIDTH * self.length_scaler / 2
                        + KG_DIVIDER_WIDTH * self.length_scaler / 2,
                        0,
                    ),
                    (
                        KG_BOARD_WIDTH * self.length_scaler / 2
                        + KG_DIVIDER_WIDTH * self.length_scaler / 2,
                        KG_BOARD_HEIGHT * self.length_scaler,
                    ),
                ]
            ),
        )
        self.bodies["ground"] = self.world.CreateStaticBody(position=(0, 0))

        self.bodies["divider_left"].fixtures[0].filterData.categoryBits = 0x0010
        self.bodies["divider_right"].fixtures[0].filterData.categoryBits = 0x0010

        # Create dynamic bodies
        self.bodies["puck1"] = self.world.CreateDynamicBody(
            position=(
                KG_BOARD_WIDTH * self.length_scaler / 3,
                KG_BOARD_HEIGHT * self.length_scaler / 2,
            ),
            fixedRotation=True,
            bullet=True,
        )
        self.bodies["puck1"].CreateCircleFixture(
            radius=KG_PUCK_RADIUS * self.length_scaler,
            restitution=0.0,
            userData=self.FixtureUserData("puck1", KG_PUCK_COLOR),
            density=KG_PUCK_MASS / (pi * (KG_PUCK_RADIUS * self.length_scaler) ** 2),
        )

        self.bodies["puck2"] = self.world.CreateDynamicBody(
            position=(
                2 * KG_BOARD_WIDTH * self.length_scaler / 3,
                KG_BOARD_HEIGHT * self.length_scaler / 2,
            ),
            fixedRotation=True,
            bullet=True,
        )
        self.bodies["puck2"].CreateCircleFixture(
            radius=KG_PUCK_RADIUS * self.length_scaler,
            restitution=0.0,
            userData=self.FixtureUserData("puck2", KG_PUCK_COLOR),
            density=KG_PUCK_MASS / (pi * (KG_PUCK_RADIUS * self.length_scaler) ** 2),
        )

        ball_start_positions_dict = {
            "top_right": (
                KG_BOARD_WIDTH * self.length_scaler
                - KG_CORNER_RADIUS * self.length_scaler / 2,
                KG_BOARD_HEIGHT * self.length_scaler
                - KG_CORNER_RADIUS * self.length_scaler / 2,
            ),
            "bottom_right": (
                KG_BOARD_WIDTH * self.length_scaler
                - KG_CORNER_RADIUS * self.length_scaler / 2,
                KG_CORNER_RADIUS * self.length_scaler / 2,
            ),
            "top_left": (
                KG_CORNER_RADIUS * self.length_scaler / 2,
                KG_BOARD_HEIGHT * self.length_scaler
                - KG_CORNER_RADIUS * self.length_scaler / 2,
            ),
            "bottom_left": (
                KG_CORNER_RADIUS * self.length_scaler / 2,
                KG_CORNER_RADIUS * self.length_scaler / 2,
            ),
        }
        ball_start_positions_dict["random"] = random.choice(
            list(ball_start_positions_dict.values())
        )

        self.bodies["ball"] = self.world.CreateDynamicBody(
            position=ball_start_positions_dict[ball_start_position], bullet=True
        )
        self.bodies["ball"].CreateCircleFixture(
            radius=KG_BALL_RADIUS * self.length_scaler,
            restitution=KG_RESTITUTION_COEF,
            userData=self.FixtureUserData("ball", KG_BALL_COLOR),
            density=KG_BALL_MASS / (pi * (KG_BALL_RADIUS * self.length_scaler) ** 2),
            maskBits=0xFF0F,
        )

        self.bodies["biscuit1"] = self.world.CreateDynamicBody(
            position=(
                KG_BOARD_WIDTH * self.length_scaler / 2,
                KG_BOARD_HEIGHT * self.length_scaler / 2,
            ),
            bullet=True,
        )
        self.bodies["biscuit1"].CreateCircleFixture(
            radius=KG_BISCUIT_RADIUS * self.length_scaler,
            restitution=KG_RESTITUTION_COEF,
            userData=self.FixtureUserData("biscuit1", KG_BISCUIT_COLOR),
            density=KG_BISCUIT_MASS
            / (pi * (KG_BISCUIT_RADIUS * self.length_scaler) ** 2),
            maskBits=0xFF0F,
        )

        self.bodies["biscuit2"] = self.world.CreateDynamicBody(
            position=(
                KG_BOARD_WIDTH * self.length_scaler / 2,
                (KG_BOARD_HEIGHT * self.length_scaler / 2)
                + KG_BISCUIT_START_OFFSET_Y * self.length_scaler,
            ),
            bullet=True,
        )
        self.bodies["biscuit2"].CreateCircleFixture(
            radius=KG_BISCUIT_RADIUS * self.length_scaler,
            restitution=KG_RESTITUTION_COEF,
            userData=self.FixtureUserData("biscuit2", KG_BISCUIT_COLOR),
            density=KG_BISCUIT_MASS
            / (pi * (KG_BISCUIT_RADIUS * self.length_scaler) ** 2),
            maskBits=0xFF0F,
        )

        self.bodies["biscuit3"] = self.world.CreateDynamicBody(
            position=(
                KG_BOARD_WIDTH * self.length_scaler / 2,
                (KG_BOARD_HEIGHT * self.length_scaler / 2)
                - KG_BISCUIT_START_OFFSET_Y * self.length_scaler,
            ),
            bullet=True,
        )
        self.bodies["biscuit3"].CreateCircleFixture(
            radius=KG_BISCUIT_RADIUS * self.length_scaler,
            restitution=KG_RESTITUTION_COEF,
            userData=self.FixtureUserData("biscuit3", KG_BISCUIT_COLOR),
            density=KG_BISCUIT_MASS
            / (pi * (KG_BISCUIT_RADIUS * self.length_scaler) ** 2),
            maskBits=0xFF0F,
        )

        # Create groupings
        self.magnet_bodies = ["biscuit1", "biscuit2", "biscuit3"]
        self.render_bodies = [
            "puck1",
            "puck2",
            "ball",
            "biscuit1",
            "biscuit2",
            "biscuit3",
        ]

        # Create joints
        self.world.CreateFrictionJoint(
            bodyA=self.bodies["ground"],
            bodyB=self.bodies["ball"],
            maxForce=self.bodies["ball"].mass * KG_GRAVITY,
        )
        self.world.CreateFrictionJoint(
            bodyA=self.bodies["ground"],
            bodyB=self.bodies["biscuit1"],
            maxForce=self.bodies["biscuit1"].mass * KG_GRAVITY,
        )
        self.world.CreateFrictionJoint(
            bodyA=self.bodies["ground"],
            bodyB=self.bodies["biscuit2"],
            maxForce=self.bodies["biscuit2"].mass * KG_GRAVITY,
        )
        self.world.CreateFrictionJoint(
            bodyA=self.bodies["ground"],
            bodyB=self.bodies["biscuit3"],
            maxForce=self.bodies["biscuit3"].mass * KG_GRAVITY,
        )

        # Update internal state variable
        self.is_initialized = True

        # Render frame
        frame = self.__render_frame()

        # Determine game states
        game_states = self.__determine_game_state()

        # Determine agent states
        agent_states = self.__determine_agent_state()

        # Return environment state information
        return frame, game_states, agent_states

    def step(self, action1, action2):
        # Check that reset() is called before step()
        assert self.is_initialized

        # Check action types
        assert isinstance(action1, tuple)
        assert isinstance(action2, tuple)

        # Apply forces to puck1
        self.bodies["puck1"].ApplyLinearImpulse(
            action1, self.bodies["puck1"].position, wake=True
        )

        # Apply forces to puck2
        self.bodies["puck2"].ApplyLinearImpulse(
            action2, self.bodies["puck2"].position, wake=True
        )

        # Apply magnetic forces to biscuits
        for body_key in self.magnet_bodies:
            self.__apply_magnet_force(self.bodies["puck1"], self.bodies[body_key])
            self.__apply_magnet_force(self.bodies["puck2"], self.bodies[body_key])

        # Step the physics simulation
        self.world.Step(
            self.time_step, self.velocity_iterations, self.position_iterations
        )

        # Handle resultant puck to biscuit collisions
        while self.world.contactListener.collision_list:
            # Retrieve fixtures
            puck, biscuit = self.world.contactListener.collision_list.pop()

            # Compute new biscuit position
            position = biscuit.body.position - puck.body.position

            # FIXME: results in a very small jump in position, but ensures the distance from puck to biscuit is always the same after collision
            # position.Normalize()
            # position = position * (puck.shape.radius + biscuit.shape.radius)

            # Create new biscuit fixture
            new_biscuit = puck.body.CreateCircleFixture(
                radius=biscuit.shape.radius, pos=position, userData=biscuit.userData
            )
            new_biscuit.sensor = True

            # Remove old biscuit body
            self.magnet_bodies.remove(biscuit.userData.name)
            self.render_bodies.remove(biscuit.userData.name)
            del self.bodies[biscuit.userData.name]
            self.world.DestroyBody(biscuit.body)

        # Render the resulting frame
        frame = self.__render_frame()

        # Determine game states
        game_states = self.__determine_game_state()

        # Determine agent states
        agent_states = self.__determine_agent_state()

        # Return environment state information
        return frame, game_states, agent_states

    def __determine_agent_state(self):
        # Creates a state dict of all the agents in the environment

        def __get_biscuit_state(biscuit_name):
            # Get biscuit states
            biscuit_pos_x = biscuit_pos_y = biscuit_vel_x = biscuit_vel_y = None
            if biscuit_name in self.bodies:
                biscuit_pos_x = self.bodies[biscuit_name].position.x
                biscuit_pos_y = self.bodies[biscuit_name].position.y
                biscuit_vel_x = self.bodies[biscuit_name].linearVelocity.x
                biscuit_vel_y = self.bodies[biscuit_name].linearVelocity.y
            else:
                # Find fixture with userData.name == biscuit1
                fixture = next(
                    obj
                    for obj in [
                        next(
                            (
                                obj
                                for obj in self.bodies["puck1"].fixtures
                                if obj.userData.name == biscuit_name
                            ),
                            None,
                        ),
                        next(
                            (
                                obj
                                for obj in self.bodies["puck2"].fixtures
                                if obj.userData.name == biscuit_name
                            ),
                            None,
                        ),
                    ]
                    if obj is not None
                )
                biscuit_pos_x = fixture.body.position.x + fixture.shape.pos.x
                biscuit_pos_y = fixture.body.position.y + fixture.shape.pos.y
                biscuit_vel_x = fixture.body.linearVelocity.x
                biscuit_vel_y = fixture.body.linearVelocity.y

            return biscuit_pos_x, biscuit_pos_y, biscuit_vel_x, biscuit_vel_y

        # Get biscuit 1 states
        biscuit1_pos_x, biscuit1_pos_y, biscuit1_vel_x, biscuit1_vel_y = (
            __get_biscuit_state("biscuit1")
        )

        # Get biscuit 2 states
        biscuit2_pos_x, biscuit2_pos_y, biscuit2_vel_x, biscuit2_vel_y = (
            __get_biscuit_state("biscuit2")
        )

        # Get biscuit 3 states
        biscuit3_pos_x, biscuit3_pos_y, biscuit3_vel_x, biscuit3_vel_y = (
            __get_biscuit_state("biscuit3")
        )

        # Get puck 1 states
        puck1_pos_x = self.bodies["puck1"].position.x
        puck1_pos_y = self.bodies["puck1"].position.y
        puck1_vel_x = self.bodies["puck1"].linearVelocity.x
        puck1_vel_y = self.bodies["puck1"].linearVelocity.y

        # Get puck 2 states
        puck2_pos_x = self.bodies["puck2"].position.x
        puck2_pos_y = self.bodies["puck2"].position.y
        puck2_vel_x = self.bodies["puck2"].linearVelocity.x
        puck2_vel_y = self.bodies["puck2"].linearVelocity.y

        # Get ball states
        ball_pos_x = self.bodies["ball"].position.x
        ball_pos_y = self.bodies["ball"].position.y
        ball_vel_x = self.bodies["ball"].linearVelocity.x
        ball_vel_y = self.bodies["ball"].linearVelocity.y

        # Create state dict
        state_dict = {
            "biscuit1_pos_x": biscuit1_pos_x,
            "biscuit1_pos_y": biscuit1_pos_y,
            "biscuit1_vel_x": biscuit1_vel_x,
            "biscuit1_vel_y": biscuit1_vel_y,
            "biscuit2_pos_x": biscuit2_pos_x,
            "biscuit2_pos_y": biscuit2_pos_y,
            "biscuit2_vel_x": biscuit2_vel_x,
            "biscuit2_vel_y": biscuit2_vel_y,
            "biscuit3_pos_x": biscuit3_pos_x,
            "biscuit3_pos_y": biscuit3_pos_y,
            "biscuit3_vel_x": biscuit3_vel_x,
            "biscuit3_vel_y": biscuit3_vel_y,
            "puck1_pos_x": puck1_pos_x,
            "puck1_pos_y": puck1_pos_y,
            "puck1_vel_x": puck1_vel_x,
            "puck1_vel_y": puck1_vel_y,
            "puck2_pos_x": puck2_pos_x,
            "puck2_pos_y": puck2_pos_y,
            "puck2_vel_x": puck2_vel_x,
            "puck2_vel_y": puck2_vel_y,
            "ball_pos_x": ball_pos_x,
            "ball_pos_y": ball_pos_y,
            "ball_vel_x": ball_vel_x,
            "ball_vel_y": ball_vel_y,
        }

        # Convert to pixel coordinates
        process_state = lambda x: x * self.pixels_per_meter
        state_dict.update(
            (key, process_state(value)) for key, value in state_dict.items()
        )

        return state_dict

    def __determine_game_state(self):
        # Determines the state of the game
        states = []

        # Determine puck 1 win conditions
        if self.__is_in_goal(self.bodies["ball"])[1]:
            states.append(self.GameStates.P1_SCORE)

        if self.__is_in_goal(self.bodies["puck2"])[1]:
            states.append(self.GameStates.P2_KLASK)

        if self.__num_biscuits_on_puck(self.bodies["puck2"]) >= 2:
            states.append(self.GameStates.P2_TWO_BISCUIT)

        p1_win_states = {
            self.GameStates.P1_SCORE,
            self.GameStates.P2_KLASK,
            self.GameStates.P2_TWO_BISCUIT,
        }
        if set.intersection(p1_win_states, states):
            states.append(self.GameStates.P1_WIN)

        # Determine puck 2 win conditions
        if self.__is_in_goal(self.bodies["ball"])[0]:
            states.append(self.GameStates.P2_SCORE)

        if self.__is_in_goal(self.bodies["puck1"])[0]:
            states.append(self.GameStates.P1_KLASK)

        if self.__num_biscuits_on_puck(self.bodies["puck1"]) >= 2:
            states.append(self.GameStates.P1_TWO_BISCUIT)

        p2_win_states = {
            self.GameStates.P2_SCORE,
            self.GameStates.P1_KLASK,
            self.GameStates.P1_TWO_BISCUIT,
        }
        if set.intersection(p2_win_states, states):
            states.append(self.GameStates.P2_WIN)

        # Determine if win condition was met
        if not len(states):
            states.append(self.GameStates.PLAYING)

        return states

    def __num_biscuits_on_puck(self, puck_body):
        # Get the number of biscuits attached to a puck
        return len(puck_body.fixtures) - 1

    def __is_in_goal(self, body):
        # Determine if the puck/ball/biscuit is inside the goal

        # Define return type, idx 0 is left goal, idx 1 is right goal
        response = [False, False]

        # Determine if body in left goal
        if (
            dist(
                body.position,
                (
                    KG_GOAL_OFFSET_X * self.length_scaler,
                    (KG_BOARD_HEIGHT / 2) * self.length_scaler,
                ),
            )
            <= KG_GOAL_RADIUS * self.length_scaler
        ):
            response[0] = True

        # Determine if body in right goal
        if (
            dist(
                body.position,
                (
                    (KG_BOARD_WIDTH - KG_GOAL_OFFSET_X) * self.length_scaler,
                    (KG_BOARD_HEIGHT / 2) * self.length_scaler,
                ),
            )
            <= KG_GOAL_RADIUS * self.length_scaler
        ):
            response[1] = True

        return response

    def __apply_magnet_force(self, puck_body, biscuit_body):
        # Get the distance vector between the two bodies
        force = puck_body.position - biscuit_body.position

        # Normalize the distance vector and get the Euclidean distance between the two bodies
        separation = force.Normalize()

        # Compute magnetic force between two points
        force *= (KG_PERMEABILITY_AIR * KG_MAGNETIC_CHARGE**2) / (
            4 * pi * separation**2
        )

        # Apply forces to bodies
        biscuit_body.ApplyForceToCenter(force=force, wake=True)

    def __render_frame(self):
        # Determine if rendering enabled
        if self.render_mode is None:
            return None

        # Import PyGame
        with redirect_stdout(None):
            global pygame
            import pygame

        # Setup PyGame if needed
        if self.screen is None and self.render_mode in ["human", "human_unclocked"]:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
            pygame.display.set_caption("Klask Simulator")
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        # Render game board surface
        if self.game_board is None:
            self.game_board = self.__render_game_board()

        # Create a new surface
        surface = pygame.Surface((self.screen_width, self.screen_height), 0, 32)

        # Display the game board
        surface.blit(self.game_board, (0, 0))

        # Display the bodies
        for body_key in self.render_bodies:
            for fixture in self.bodies[body_key]:
                self.__render_circle_fixture(fixture, surface)

        # Display to screen if needed
        if self.render_mode in ["human", "human_unclocked"]:
            # Display surface to screen
            self.screen.blit(surface, (0, 0))
            pygame.event.pump()
            pygame.display.flip()

            # Manage frame rate
            if self.render_mode == "human":
                self.clock.tick(self.display_fps)

        # Return rendered frame as numpy array (RGB order)
        return pygame.surfarray.array3d(surface).swapaxes(0, 1)

    def __render_circle_fixture(self, circle, surface):
        # Render a circle fixture onto a surface
        position = circle.body.transform * circle.shape.pos * self.pixels_per_meter
        position = (position[0], self.screen_height - position[1])
        pygame.draw.circle(
            surface,
            circle.userData.color,
            [int(x) for x in position],
            int(circle.shape.radius * self.pixels_per_meter),
        )

    def __render_game_board(self):
        # Create a new surface
        surface = pygame.Surface((self.screen_width, self.screen_height), 0, 32)

        # Render Game Board
        pygame.draw.rect(
            surface,
            KG_BOARD_COLOR,
            pygame.Rect(0, 0, self.screen_width, self.screen_height),
        )

        # Render Goals
        pygame.draw.circle(
            surface,
            KG_GOAL_COLOR,
            (
                KG_GOAL_OFFSET_X * self.pixels_per_meter * self.length_scaler,
                (KG_BOARD_HEIGHT / 2) * self.pixels_per_meter * self.length_scaler,
            ),
            KG_GOAL_RADIUS * self.pixels_per_meter * self.length_scaler,
        )
        pygame.draw.circle(
            surface,
            KG_GOAL_COLOR,
            (
                (KG_BOARD_WIDTH - KG_GOAL_OFFSET_X)
                * self.pixels_per_meter
                * self.length_scaler,
                (KG_BOARD_HEIGHT / 2) * self.pixels_per_meter * self.length_scaler,
            ),
            KG_GOAL_RADIUS * self.pixels_per_meter * self.length_scaler,
        )

        # Render Corners
        pygame.draw.circle(
            surface,
            KG_CORNER_COLOR,
            (0, 0),
            KG_CORNER_RADIUS * self.pixels_per_meter * self.length_scaler,
            int(KG_CORNER_THICKNESS * self.pixels_per_meter * self.length_scaler),
        )
        pygame.draw.circle(
            surface,
            KG_CORNER_COLOR,
            (KG_BOARD_WIDTH * self.pixels_per_meter * self.length_scaler, 0),
            KG_CORNER_RADIUS * self.pixels_per_meter * self.length_scaler,
            int(KG_CORNER_THICKNESS * self.pixels_per_meter * self.length_scaler),
        )
        pygame.draw.circle(
            surface,
            KG_CORNER_COLOR,
            (
                KG_BOARD_WIDTH * self.pixels_per_meter * self.length_scaler,
                KG_BOARD_HEIGHT * self.pixels_per_meter * self.length_scaler,
            ),
            KG_CORNER_RADIUS * self.pixels_per_meter * self.length_scaler,
            int(KG_CORNER_THICKNESS * self.pixels_per_meter * self.length_scaler),
        )
        pygame.draw.circle(
            surface,
            KG_CORNER_COLOR,
            (0, KG_BOARD_HEIGHT * self.pixels_per_meter * self.length_scaler),
            KG_CORNER_RADIUS * self.pixels_per_meter * self.length_scaler,
            int(KG_CORNER_THICKNESS * self.pixels_per_meter * self.length_scaler),
        )

        # Render Biscuit Start
        pygame.draw.circle(
            surface,
            KG_BISCUIT_START_COLOR,
            (
                (KG_BOARD_WIDTH / 2) * self.pixels_per_meter * self.length_scaler,
                (KG_BOARD_HEIGHT / 2) * self.pixels_per_meter * self.length_scaler,
            ),
            KG_BISCUIT_START_RADIUS * self.pixels_per_meter * self.length_scaler,
            int(
                KG_BISCUIT_START_THICKNESS * self.pixels_per_meter * self.length_scaler
            ),
        )
        pygame.draw.circle(
            surface,
            KG_BISCUIT_START_COLOR,
            (
                (KG_BOARD_WIDTH / 2) * self.pixels_per_meter * self.length_scaler,
                ((KG_BOARD_HEIGHT / 2) - KG_BISCUIT_START_OFFSET_Y)
                * self.pixels_per_meter
                * self.length_scaler,
            ),
            KG_BISCUIT_START_RADIUS * self.pixels_per_meter * self.length_scaler,
            int(
                KG_BISCUIT_START_THICKNESS * self.pixels_per_meter * self.length_scaler
            ),
        )
        pygame.draw.circle(
            surface,
            KG_BISCUIT_START_COLOR,
            (
                (KG_BOARD_WIDTH / 2) * self.pixels_per_meter * self.length_scaler,
                ((KG_BOARD_HEIGHT / 2) + KG_BISCUIT_START_OFFSET_Y)
                * self.pixels_per_meter
                * self.length_scaler,
            ),
            KG_BISCUIT_START_RADIUS * self.pixels_per_meter * self.length_scaler,
            int(
                KG_BISCUIT_START_THICKNESS * self.pixels_per_meter * self.length_scaler
            ),
        )

        # Render Game Board Logo
        pil_image = Image.open(KG_BOARD_LOGO_PATH)
        logo = pygame.image.fromstring(
            pil_image.tobytes("raw", "RGBA"), pil_image.size, "RGBA"
        )
        logo = pygame.transform.scale(
            logo,
            (
                KG_BOARD_LOGO_WIDTH * self.pixels_per_meter * self.length_scaler,
                KG_BOARD_LOGO_HEIGHT * self.pixels_per_meter * self.length_scaler,
            ),
        )

        logo_right = pygame.transform.rotate(logo, 90)
        logo_left = pygame.transform.rotate(logo, -90)

        surface.blit(
            logo_left,
            (
                ((KG_BOARD_WIDTH / 3) - KG_BOARD_LOGO_HEIGHT)
                * self.pixels_per_meter
                * self.length_scaler,
                ((KG_BOARD_HEIGHT / 2) - (KG_BOARD_LOGO_WIDTH / 2))
                * self.pixels_per_meter
                * self.length_scaler,
            ),
        )
        surface.blit(
            logo_right,
            (
                (2 * (KG_BOARD_WIDTH / 3)) * self.pixels_per_meter * self.length_scaler,
                ((KG_BOARD_HEIGHT / 2) - (KG_BOARD_LOGO_WIDTH / 2))
                * self.pixels_per_meter
                * self.length_scaler,
            ),
        )

        # Return surface
        return surface

    def close(self):
        if self.screen is not None:
            pygame.quit()


if __name__ == "__main__":
    pass
