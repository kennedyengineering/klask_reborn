# Render Klask game board using pygame

import pygame
import math

from klask_constants import *

# TODO: render_game_board() only once, then keep using it

def render_game_board(pixels_per_meter):
    # Create a new surface
    surface = pygame.Surface((KG_BOARD_WIDTH * pixels_per_meter, KG_BOARD_HEIGHT * pixels_per_meter), 0, 32)

    # Render Game Board
    pygame.draw.rect(surface, KG_BOARD_COLOR, pygame.Rect(0, 0, KG_BOARD_WIDTH * pixels_per_meter, KG_BOARD_HEIGHT * pixels_per_meter))

    # Render Goals
    pygame.draw.circle(surface, KG_GOAL_COLOR, (KG_GOAL_OFFSET_X * pixels_per_meter, (KG_BOARD_HEIGHT / 2) * pixels_per_meter), KG_GOAL_RADIUS * pixels_per_meter)
    pygame.draw.circle(surface, KG_GOAL_COLOR, ((KG_BOARD_WIDTH - KG_GOAL_OFFSET_X) * pixels_per_meter, (KG_BOARD_HEIGHT / 2) * pixels_per_meter), KG_GOAL_RADIUS * pixels_per_meter)

    # Render Corners
    pygame.draw.circle(surface, KG_CORNER_COLOR, (0, 0), KG_CORNER_RADIUS * pixels_per_meter, int(KG_CORNER_THICKNESS * pixels_per_meter))
    pygame.draw.circle(surface, KG_CORNER_COLOR, (KG_BOARD_WIDTH * pixels_per_meter, 0), KG_CORNER_RADIUS * pixels_per_meter, int(KG_CORNER_THICKNESS * pixels_per_meter))
    pygame.draw.circle(surface, KG_CORNER_COLOR, (KG_BOARD_WIDTH * pixels_per_meter, KG_BOARD_HEIGHT * pixels_per_meter), KG_CORNER_RADIUS * pixels_per_meter, int(KG_CORNER_THICKNESS * pixels_per_meter))
    pygame.draw.circle(surface, KG_CORNER_COLOR, (0, KG_BOARD_HEIGHT * pixels_per_meter), KG_CORNER_RADIUS * pixels_per_meter, int(KG_CORNER_THICKNESS * pixels_per_meter))

    # Render Biscuit Start
    pygame.draw.circle(surface, KG_BISCUIT_START_COLOR, ((KG_BOARD_WIDTH / 2) * pixels_per_meter, (KG_BOARD_HEIGHT / 2) * pixels_per_meter), KG_BISCUIT_START_RADIUS * pixels_per_meter, int(KG_BISCUIT_START_THICKNESS * pixels_per_meter))
    pygame.draw.circle(surface, KG_BISCUIT_START_COLOR, ((KG_BOARD_WIDTH / 2) * pixels_per_meter, ((KG_BOARD_HEIGHT / 2) - KG_BISCUIT_START_OFFSET_Y) * pixels_per_meter), KG_BISCUIT_START_RADIUS * pixels_per_meter, int(KG_BISCUIT_START_THICKNESS * pixels_per_meter))
    pygame.draw.circle(surface, KG_BISCUIT_START_COLOR, ((KG_BOARD_WIDTH / 2) * pixels_per_meter, ((KG_BOARD_HEIGHT / 2) + KG_BISCUIT_START_OFFSET_Y) * pixels_per_meter), KG_BISCUIT_START_RADIUS * pixels_per_meter, int(KG_BISCUIT_START_THICKNESS * pixels_per_meter))

    # Render Game Board Logo
    logo = pygame.image.load(KG_BOARD_LOGO_PATH).convert_alpha()
    logo = pygame.transform.scale(logo, (KG_BOARD_LOGO_WIDTH * pixels_per_meter, KG_BOARD_LOGO_HEIGHT * pixels_per_meter))

    logo_right = pygame.transform.rotate(logo, 90)
    logo_left = pygame.transform.rotate(logo, -90)

    surface.blit(logo_left, (((KG_BOARD_WIDTH / 3) - KG_BOARD_LOGO_HEIGHT) * pixels_per_meter, ((KG_BOARD_HEIGHT / 2) - (KG_BOARD_LOGO_WIDTH / 2)) * pixels_per_meter))
    surface.blit(logo_right, ((2 * (KG_BOARD_WIDTH / 3)) * pixels_per_meter, ((KG_BOARD_HEIGHT / 2) - (KG_BOARD_LOGO_WIDTH / 2)) * pixels_per_meter))

    # Return surface
    return surface



