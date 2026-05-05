"""
Sprites Implementations for StrandsGUI
"""

from typing import TypeAlias
from string import Formatter
import pygame
from gui_files.settings import (
    TEXT_BUFFER, ELEMENT_BUFFER, TEXT_COLOR, CANVAS_COLOR
    )
from base import PosBase

Specs: TypeAlias = tuple[int, int, int, int]


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
    """ class for all text elements in the game """

    _init: bool
    image: pygame.Surface
    rect: pygame.Rect
    text: str
    color: pygame.Color
    border: bool


    def __init__(
        self,
        text: str,
        xywh: Specs,
        border: bool = False
        ) -> None:
        """ constructor """
        self._init = True
        super().__init__()
        if not isinstance(border, bool):
            raise TypeError(
                "The argument `border` must be boolean."
                )
        self.border = border
        Text.retext(self, text, TEXT_COLOR)
        Text.resize(self, xywh)
        self._init = False
        Text.render(self)


    def _textify(self) -> None:
        """ fit and render the font """
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
        text = pygame.font.SysFont(None, size).render(
            self.text, True, self.color
            )
        width, height = tuple(self.rect.size)
        self.image.blit(
            text,
            ((width - w) / 2, (height - h) / 2)
            )


    def _initify(self) -> None:
        """ create the surface """
        self.image = pygame.Surface(
            self.rect.size,
            pygame.SRCALPHA
            )
        self.image.fill(set_alpha(CANVAS_COLOR, 0))


    def _bordify(self) -> None:
        """ draw a border """
        rect = self.image.get_rect().scale_by(
                ELEMENT_BUFFER, ELEMENT_BUFFER
                )
        border_radius = round(max(1, min(*rect.size) / 12))
        pygame.draw.rect(
            self.image,
            self.color,
            rect,
            2,
            border_radius = border_radius
            )


    def resize(self, xywh: Specs) -> None:
        """ update the size and/or position """
        if (
            not isinstance(xywh, tuple)
            or any(not isinstance(n, int) for n in xywh)
            ):
            raise TypeError(
                "The argument `xywh` must be a tuple of 4 \
                integer."
                )
        if self._init:
            self.rect = pygame.Rect(*xywh)
        else:
            self.rect.update(*xywh)
        self.rect.scale_by_ip(
            ELEMENT_BUFFER, ELEMENT_BUFFER
            )
        if not self._init:
            Text.render(self)


    def retext(
        self,
        text: str,
        color: pygame.Color | None = None
        ) -> None:
        """ update the text """
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
        if not self._init:
            Text.render(self)


    def render(self) -> None:
        """ update the image """
        Text._initify(self)
        Text._textify(self)


class Letter(Text):
    """ class for all letter elements in the game """

    # _init: bool
    # image: pygame.Surface
    # rect: pygame.Rect
    # text: str
    # color: pygame.Color
    highlight_primary: pygame.Color | None
    highlight_secondary: pygame.Color | None
    position: PosBase


    def __init__(
        self, pos: PosBase, ch: str, xywh: Specs
        ) -> None:
        """ constructor """
        super().__init__(ch, xywh)
        self._init = True
        if not isinstance(pos, PosBase):
            raise TypeError(
                "The argument `pos` must be a PosBase \
                object."
                )
        self.position = pos
        self.highlight_primary = None
        self.highlight_secondary = None
        self._init = False
        Letter.render(self)


    def update(
        self,
        xb: int,
        yb: int,
        w: int,
        h: int
        ) -> None:
        """ update the size and/or position """
        Letter.resize(
            self,
            (
                xb + self.position.c * w,
                yb + self.position.r * h,
                w,
                h
                )
            )
        Letter.render(self)


    def _highlightify(self) -> None:
        """ highlight a letter """
        if self.highlight_primary is not None:
            highlight = self.highlight_primary
        elif self.highlight_secondary is not None:
            highlight = self.highlight_secondary
        else:
            highlight = None
        if highlight is not None:
            pygame.draw.circle(
                self.image,
                highlight,
                self.image.get_rect().center,
                1/2 * ELEMENT_BUFFER * min(self.rect.size)
                )


    def render(self) -> None:
        """ update the image """
        Letter._initify(self)
        Letter._highlightify(self)
        if self.border:
            Letter._bordify(self)
        Letter._textify(self)


class Meter(Text):
    """ class for a meter element in the game """

    # _init: bool
    # image: pygame.Surface
    # rect: pygame.Rect
    # text: str
    # color: pygame.Color
    textform: str | None
    progress: int
    threshold: int
    use_bar: bool


    def __init__(
        self,
        text: str,
        xywh: Specs,
        threshold: int,
        use_bar: bool = False
        ) -> None:
        """ constructor """
        super().__init__(text, xywh)
        self._init = True

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
        if parameters == {'progress', 'threshold'}:
            self.textform = text
        else:
            self.textform = None

        Meter.reprogress(self, 0)

        self._init = False
        Meter.render(self)


    def reprogress(self, progress: int) -> None:
        """
        update the progress

        If the argument `progress` is greater than
        self.threshold, then self.progress is updated
        to match the threshold.
        """
        assert isinstance(progress, int) \
            and progress >= 0, \
            "The argument `progress` must be a \
            nonnegative integer."
        self.progress = min(progress, self.threshold)
        if self.textform is not None:
            self.retext(self.textform.format(
                progress = self.progress,
                threshold = self.threshold
            ))
        if not self._init:
            Meter.render(self)


    def render(self) -> None:
        """ update the image """
        Meter._initify(self)
        if self.use_bar:
            Meter._barify(self)
        elif self.border:
            Meter._bordify(self)
        Meter._textify(self)


    def _barify(self) -> None:
        """ create a progress bar """
        rect = self.image.get_rect().scale_by(
            ELEMENT_BUFFER, ELEMENT_BUFFER
            )
        border_radius = round(max(1, min(*rect.size) / 12))
        pygame.draw.rect(
            self.image,
            set_alpha(self.color, 128),
            rect.scale_by(
                self.progress / self.threshold, 1
                ),
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
