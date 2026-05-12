"""
All constants for the GUI Implementation
"""

import pygame


HINT_THRESHOLD = 3
"""
the number of non-theme words to find before receiving a
hint
"""

CAPTION = "Strands"
""" the caption for the pygame window """

FRAME_RATE: int = 24
""" the refresh rate for the pygame window """

CANVAS_SIZE: tuple[int, int] = (600, 600)
""" the minimum pygame window size when launching """

GRID_SIZE: int = 60
""" the standard spacing of letters on the board """

HEADER = 50
""" the standard height for the header of the board """

FOOTER = 50
""" the standard height for the footer of the board """

BORDER: int = 25
""" the standard size for the border around the board """

TEXT_BUFFER: float = 1
"""
used by Text sprites to scale text to add a margin around
the text displayed
"""

ELEMENT_BUFFER: float = 1 - 1/4
"""
used by StrandsGUI to scale sprites to add space between
and around sprites in the pygame window
"""

CANVAS_COLOR: pygame.Color = pygame.Color("white")
""" the background color of the canvas """

TEXT_COLOR: pygame.Color = pygame.Color("black")
""" the default color of text """

SELECT_COLOR: pygame.Color = pygame.Color("lightgray")
""" the color used to show selected strands """

UNTHEME_COLOR: pygame.Color = pygame.Color("lightgray")
""" the color used to show dictionary words when found """

HINT_COLOR: pygame.Color = pygame.Color("lavender")
""" the color used to show active hints """

FOUND_COLOR: pygame.Color = pygame.Color("lightskyblue")
""" the color used to show found words """

BORDER_COLOR: pygame.Color = pygame.Color("snow2")
""" the color of the border around the board """
