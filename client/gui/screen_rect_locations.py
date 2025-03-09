

import pygame
from client import consts


SCREEN_CENTER = (consts.WINDOW_DIMENSIONS["width"] / 2, consts.WINDOW_DIMENSIONS["height"] / 2)


TOP_LEFT_RECT = pygame.rect.Rect(
        0,0,
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )
TOP_MIDDLE_RECT = pygame.rect.Rect(
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        0,
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )
TOP_RIGHT_RECT = pygame.rect.Rect(
        2*(consts.WINDOW_DIMENSIONS["width"] / 3),
        0,
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )
MIDDLE_LEFT_RECT = pygame.rect.Rect(
        0,
        SCREEN_CENTER[1] - (consts.WINDOW_DIMENSIONS["height"] / 10),
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )
CENTER_RECT = pygame.rect.Rect(
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        SCREEN_CENTER[1] - (consts.WINDOW_DIMENSIONS["height"] / 10),
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )
MIDDLE_RIGHT_RECT = pygame.rect.Rect(
        2*(consts.WINDOW_DIMENSIONS["width"] / 3),
        SCREEN_CENTER[1] - (consts.WINDOW_DIMENSIONS["height"] / 10),
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )
BOTTOM_LEFT_RECT = pygame.rect.Rect(
        0,
        consts.WINDOW_DIMENSIONS["height"] - (consts.WINDOW_DIMENSIONS["height"] / 5),
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )
BOTTOM_MIDDLE_RECT = pygame.rect.Rect(
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        consts.WINDOW_DIMENSIONS["height"] - (consts.WINDOW_DIMENSIONS["height"] / 5),
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )
BOTTOM_RIGHT_RECT = pygame.rect.Rect(
        2*(consts.WINDOW_DIMENSIONS["width"] / 3),
        consts.WINDOW_DIMENSIONS["height"] - (consts.WINDOW_DIMENSIONS["height"] / 5),
        (consts.WINDOW_DIMENSIONS["width"] / 3),
        (consts.WINDOW_DIMENSIONS["height"] / 5),
    )