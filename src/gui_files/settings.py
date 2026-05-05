"""
All constants for the StrandsGUI Implementation
"""

import pygame


HINT_THRESHOLD = 3

CAPTION = "Strands"
FRAME_RATE: int = 24

CANVAS_SIZE: tuple[int, int] = (600, 600)
GRID_SIZE: int = 60
HEADER = FOOTER = 50
BORDER: int = 25

TEXT_BUFFER: float = 1 - 1/6
ELEMENT_BUFFER: float = 1 - 1/6

CANVAS_COLOR: pygame.Color = pygame.Color("white")
TEXT_COLOR: pygame.Color = pygame.Color("black")
SELECT_COLOR: pygame.Color = pygame.Color("lightgray")
HINT_COLOR: pygame.Color = pygame.Color("lightblue1")
FOUND_COLOR: pygame.Color = pygame.Color("lightblue")
