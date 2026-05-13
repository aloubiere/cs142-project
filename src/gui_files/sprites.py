"""
Sprites Implementations for StrandsGUI
"""

from typing import NamedTuple
from string import Formatter
import pygame
from gui_files.settings import (
    TEXT_BUFFER, TEXT_COLOR, CANVAS_COLOR
    )
from base import PosBase


class Specs(NamedTuple):
    """ (x, y, w, h) """
    x: int # x center
    y: int # y center
    w: int # width
    h: int # heights


def set_alpha(
    color: pygame.Color,
    a: int
    ) -> pygame.Color:
    """
    return a new pygame.Color object with the same RBG
    values as `color` but the alpha value is set to `a`.
    """
    return pygame.Color(color.r, color.g, color.b, a)


class Text(pygame.sprite.Sprite):
    """
    class for all text elements in the game

    Attributes:
        image (pygame.Surface): a pygame.Surface object
            with the sprite image drawn onto it
        rect (pygame.Rect): a Rect of the same size as
            `image` to act as a sprite hitbox and to denote
            its position on the display
        text (str): the text to display on `image`
        color (pygame.Color): the color of the text to
            display
        border (bool): whether or not to draw a border
            around the text on `image`
    """

    image: pygame.Surface
    rect: pygame.Rect
    text: str
    color: pygame.Color
    border: bool


    def __init__(
        self,
        text: str,
        specs: Specs,
        border: bool = False
        ) -> None:
        """
        constructor

        Inputs:
        - text (str): the text to display
        - specs (Specs): the x center, y center, width, and
            height defining the containing rectangle
        - border (bool): whether or not to box the text
        """
        super().__init__()
        if not isinstance(border, bool):
            raise TypeError(
                "The argument `border` must be boolean."
                )
        self.border = border
        self.retext(text, TEXT_COLOR)
        self.resize(specs)


    def _textify(self) -> None:
        """ fit and render the text """
        size = height = round(
            self.rect.height * TEXT_BUFFER
            )
        width = round(self.rect.width * TEXT_BUFFER)
        w, h = pygame.font.SysFont(
            None,
            size
            ).size(self.text)
        while w > width or h > height:
            size -= 1
            w, h = pygame.font.SysFont(
                None,
                size
                ).size(self.text)
            if size <= 0:
                break
        text = pygame.font.SysFont(None, size).render(
            self.text, True, self.color
            )
        width, height = tuple(self.rect.size)
        self.image.blit(
            text,
            ((width - w) / 2, (height - h) / 2)
            )


    def _initify(self) -> None:
        """ initialize the image surface """
        self.image = pygame.Surface(
            self.rect.size,
            pygame.SRCALPHA
            )
        self.image.fill(set_alpha(CANVAS_COLOR, 0))


    def _bordify(self) -> None:
        """
        draw a rectangular border with rounded corners
        """
        rect = self.image.get_rect()
        border_radius = round(max(1, min(*rect.size) / 12))
        pygame.draw.rect(
            self.image,
            self.color,
            rect,
            2,
            border_radius = border_radius
            )


    def resize(self, specs: Specs) -> None:
        """
        update the size and/or position of the rectangle
        containing the text

        Inputs:
        - specs (Specs): the x center, y center, width,
            and height defining the containing rectangle
        """
        if (
            not isinstance(specs, tuple)
            or any(not isinstance(n, int) for n in specs)
            ):
            raise TypeError(
                "The argument `specs` must be of the type \
                Specs."
                )
        self.rect = pygame.Rect(0, 0, specs.w, specs.h)
        self.rect.center = (specs.x, specs.y)


    def retext(
        self,
        text: str,
        color: pygame.Color | None = None
        ) -> None:
        """
        update the text

        Inputs:
        - text (str): the text to display
        - color (pygame.Color | None): the color to change
            the text to, or None to keep the current color
        """
        if not isinstance(text, str):
            raise TypeError(
                "The argument `text` must be a string."
                )
        self.text = text
        if color is not None:
            if not isinstance(color, pygame.Color):
                raise TypeError(
                    "The argument `color` must be a \
                    pygame.Color object or None."
                    )
            self.color = color


    def render(self) -> None:
        """ render the image """
        self._initify()
        if self.border:
            self._bordify()
        self._textify()


class Letter(Text):
    """
    class for all letter elements in the game

    Attributes:
        image (pygame.Surface): a pygame.Surface object
            with the sprite image drawn onto it
        rect (pygame.Rect): a Rect of the same size as
            `image` to act as a sprite hitbox and to denote
            its position on the display
        text (str): a single character of text to display
            on `image`
        color (pygame.Color): the color of the text to
            display
        border (bool): whether or not to draw a border
            around the text on `image`
        highlight1 (pygame.Color | None): the primary
            highlight color, or None to default to the
            secondary highlight color, `highlight2`
        highlight2 (pygame.Color | None): the secondary
            highlight color, only used if the primary
            highlight color, `highlight2`, is None, or
            None to default to no highlight
        position (PosBase): the position of the letter on
            the game board
    """

    # image: pygame.Surface
    # rect: pygame.Rect
    # text: str
    # color: pygame.Color
    # border: bool
    highlight1: pygame.Color | None
    highlight2: pygame.Color | None
    position: PosBase


    def __init__(
        self, pos: PosBase, ch: str, specs: Specs
        ) -> None:
        """
        constructor

        Inputs:
        - pos (PosBase): the position on the board
        - ch (str): the letter to display
        - specs (Specs): the x center, y center, width,
            and height defining the containing rectangle
        """
        super().__init__(ch, specs)
        if not isinstance(pos, PosBase):
            raise TypeError(
                "The argument `pos` must be a PosBase \
                object."
                )
        self.position = pos
        self.highlight1 = None
        self.highlight2 = None


    def update(
        self,
        offset: tuple[int, int] | int,
        spacing: tuple[int, int] | int,
        size: tuple[int, int] | int
        ) -> None:
        """
        update the size and/or position using the
        `position` attribute


        Inputs:
            offset (int | tuple[int, int]): the new x
                and y offsets as a tuple of integers in
                that order or, if both offsets are the
                same, one integer for both
            spacing (int | tuple[int, int]): the new x
                and y spacings between positions as a
                tuple of integers in that order, or, if
                both spacings are the same, one integer
                for both
            size (int | tuple[int, int]): the new width
                and height values as a tuple of integers
                in that order, or, if both values are the
                same, one integer for both
        """
        if (
            isinstance(offset, tuple)
            and len(offset) == 2
            and all(isinstance(n, int) for n in offset)
            ):
            xb, yb = offset
        elif isinstance(offset, int):
            xb = yb = offset
        else:
            raise ValueError(
                "The argument `offset` must be an "
                "integer or a tuple of two integers."
                )
        if (
            isinstance(spacing, tuple)
            and len(spacing) == 2
            and all(isinstance(n, int) for n in spacing)
            ):
            sx, sy = spacing
        elif isinstance(spacing, int):
            sx = sy = spacing
        else:
            raise ValueError(
                "The argument `spacing` must be an "
                "integer or a tuple of two integers."
                )
        if (
            isinstance(size, tuple)
            and len(size) == 2
            and all(isinstance(n, int) for n in size)
            ):
            w, h = size
        elif isinstance(size, int):
            w = h = size
        else:
            raise ValueError(
                "The argument `size` must be an "
                "integer or a tuple of two integers."
                )
        self.resize(Specs(
            round(xb + (self.position.c + 1/2) * sx),
            round(yb + (self.position.r + 1/2) * sy),
            w, h
            ))
        self.render()


    def _highlightify(self) -> None:
        """ highlight a letter """
        if self.highlight1 is not None:
            highlight = self.highlight1
        elif self.highlight2 is not None:
            highlight = self.highlight2
        else:
            highlight = None
        if highlight is not None:
            pygame.draw.circle(
                self.image,
                highlight,
                self.image.get_rect().center,
                1/2 * min(self.rect.size)
                )


    def _bordify(self) -> None:
        """ draw a circular border """
        pygame.draw.circle(
            self.image,
            self.color,
            self.image.get_rect().center,
            1/2 * max(self.rect.size),
            2
            )


    def retext(
        self,
        text: str,
        color: pygame.Color | None = None
        ) -> None:
        """
        update the text

        Inputs:
        - text (str): a single character of text to display
        - color (pygame.Color | None): the color to change
            the text to, or None to keep the current color

        Raises ValueError if the inputted string `text` has
        more than 1 character.
        """
        super().retext(text, color)
        if len(text) > 1:
            raise ValueError(
                "Letter objects may not contain more than \
                1 character of text."
                )


    def render(self) -> None:
        """ render the image """
        self._initify()
        self._highlightify()
        if self.border:
            self._bordify()
        self._textify()


class Meter(Text):
    """
    class for a meter element in the game

    Attributes:
        image (pygame.Surface): a pygame.Surface object
            with the sprite image drawn onto it
        rect (pygame.Rect): a Rect of the same size as
            `image` to act as a sprite hitbox and to denote
            its position on the display
        text (str): the text to display on `image`
        color (pygame.Color): the color of the text to
            display
        border (bool): whether or not to draw a border
            around the text on `image`
        textform (str | None): a string with the formatting
            parameters 'meter' and 'threshold' used to
            update `text` with the current meter value, or
            None if `text` is not used to display the
            current meter values
        meter (int): the meter value as a nonnegative
            integer less than `threshold`
        threshold (int): a positive integer threshold
        use_bar (bool): whether or not to show the current
            meter value as a loading bar
    """

    # image: pygame.Surface
    # rect: pygame.Rect
    # text: str
    # color: pygame.Color
    # border: bool
    textform: str | None
    meter: int
    threshold: int
    use_bar: bool


    def __init__(
        self,
        text: str,
        specs: Specs,
        threshold: int,
        use_bar: bool = False
        ) -> None:
        """
        constructor

        Inputs:
        - text (str): the text to display
        - specs (Specs): the x center, y center, width,
            and height defining the containing rectangle
        - threshold (int): a positive integer representing
            the meter threshold
        - use_bar (bool): whether or not to show a loading
            bar

        Raises ValueError if the argument `threshold` is
        not positive.
        """
        super().__init__(text, specs)
        if not isinstance(use_bar, bool):
            raise TypeError(
                "The argument `use_bar` must be boolean."
                )
        self.use_bar = use_bar
        if not isinstance(threshold, int):
            raise TypeError(
                "The argument `threshold` must be a \
                positive integer."
                )
        if not threshold > 0:
            raise ValueError(
                "The argument `threshold` must be a \
                positive integer."
                )
        self.threshold = threshold
        parameters = set(
            field for _, field, _, _
            in Formatter().parse(text)
            )
        if parameters == {'meter', 'threshold'}:
            self.textform = text
        else:
            self.textform = None
        self.remeter(0)


    def remeter(self, meter: int) -> None:
        """
        update the meter

        If the argument `meter` is greater than
        `threshold`, then `meter` is updated
        to match the `threshold`. If the argument `meter`
        is less than 0, then `meter` is updated to be 0.
        """
        assert isinstance(meter, int), \
            "The argument `progress` must be an integer."
        self.meter = max(min(meter, self.threshold), 0)
        if self.textform is not None:
            self.retext(self.textform.format(
                meter = self.meter,
                threshold = self.threshold
            ))


    def render(self) -> None:
        """ render the image """
        self._initify()
        if self.use_bar:
            self._barify()
        elif self.border:
            self._bordify()
        self._textify()


    def _barify(self) -> None:
        """ create a progress bar """
        rect = self.image.get_rect()
        fill = rect.scale_by(self.meter / self.threshold, 1)
        fill.topleft = rect.topleft
        border_radius = round(max(1, min(*rect.size) / 12))
        if self.meter == self.threshold:
            pygame.draw.rect(
                self.image,
                set_alpha(self.color, 128),
                fill,
                border_radius = border_radius
                )
        else:
            pygame.draw.rect(
                self.image,
                set_alpha(self.color, 128),
                fill,
                border_top_left_radius = border_radius,
                border_bottom_left_radius = border_radius
                )
        pygame.draw.rect(
            self.image,
            self.color,
            rect,
            2,
            border_radius = border_radius
            )
