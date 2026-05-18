"""
Sprites Implementations for StrandsGUI
"""

from typing import NamedTuple, Any
from string import Formatter
import pygame
from base import PosBase


class SpecsBase(NamedTuple):
    """ (x, y, w, h) """
    x: int # x center
    y: int # y center
    w: int # width
    h: int # heights


class Specs(SpecsBase):
    """ (x, y, w, h) """
    def __new__(
        cls, x: int, y: int, w: int, h: int
        ) -> "Specs":
        """ verify values first """
        def check(var: str, val: Any) -> None:
            """
            helper function to verify values

            Inputs:
                var (str): the string name of the
                    variable being checked
                val (Any): the value to verify
            """
            assert (
                isinstance(var, str)
                and var in ["x", "y", "w", "h"]
                ), (
                "The argument `var` must be a string "
                "corresponding to the variable being "
                "checked."
                )
            if not isinstance(val, int):
                raise TypeError(
                    f"The attribute `{var}` must be a "
                    "nonnegative integer."
                    )
            if x < 0:
                raise ValueError(
                    f"The attribute `{var}` must be a "
                    "nonnegative integer."
                    )
        check("x", x)
        check("y", y)
        check("w", w)
        check("h", h)
        return super().__new__(cls, x, y, w, h)


class SpritesDefaults:
    """ the default values for sprite attributes """

    # the default border setting
    BORDER: bool = False

    # the default meter value
    METER: int = 0

    # the default textform value
    TEXTFORM: str | None = None

    # the default text color
    TEXT_COLOR: pygame.Color = pygame.Color("black")

    # the default buffer for text
    TEXT_BUFFER: float = 1

    # the default color key
    COLOR_KEY: pygame.Color = pygame.Color("white")

    # the default fill color for Meter objects
    FILL_COLOR: pygame.Color = pygame.Color("lightgray")

    # the default border color
    BORDER_COLOR: pygame.Color = pygame.Color("black")

    # the default highlight1 color
    HIGHLIGHT1: pygame.Color | None = None

    # the default highlight2 color
    HIGHLIGHT2: pygame.Color | None = None

    # the default ratio for size to corner radius
    ROUNDING_RATIO: float = 1/12

    # the default line width
    LINE_WIDTH: int = 2


class Text(pygame.sprite.Sprite):
    """
    class for all text elements in the game

    Attributes:
        image (pygame.Surface)
        rect (pygame.Rect)
        text (str)
        text_color (pygame.Color)
        border (bool)
        text_buffer (float)
        color_key (pygame.Color | None)
        border_color (pygame.Color)
        rounding_ratio (float)
        line_width (int)
    """

    image: pygame.Surface
    rect: pygame.Rect
    _text: str
    _text_color: pygame.Color
    _border: bool
    _text_buffer: float
    _color_key: pygame.Color | None
    _border_color: pygame.Color
    _rounding_ratio: float
    _line_width: int


    def __init__(self, text: str, specs: Specs) -> None:
        """
        constructor

        Inputs:
            text (str): the text to display
            specs (Specs): the x center, y center, width,
                and height defining the containing
                rectangle
        """
        super().__init__()
        self.text = text
        self.resize(specs)


    def _textify(self) -> None:
        """ fit and render the text """
        size = height = round(
            self.rect.height * self.text_buffer
            )
        width = round(self.rect.width * self.text_buffer)
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
            self.text, True, self.text_color
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
        if self.color_key is not None:
            self.image.fill(self.color_key)
        self.image.set_colorkey(self.color_key)


    def _bordify(self) -> None:
        """
        draw a rectangular border with rounded corners
        """
        pygame.draw.rect(
            self.image,
            self.border_color,
            self.image.get_rect(),
            self.line_width,
            round(self.rounding_ratio * min(self.rect.size))
            )


    def resize(self, specs: Specs) -> None:
        """
        update the size and/or position of the rectangle
        containing the text

        Inputs:
            specs (Specs): the x center, y center, width,
                and height defining the containing
                rectangle
        """
        if not isinstance(specs, Specs):
            raise TypeError(
                "The argument `specs` must be a Specs "
                "object."
                )
        self.rect = pygame.Rect(0, 0, specs.w, specs.h)
        self.rect.center = (specs.x, specs.y)


    def render(self) -> None:
        """ render the image """
        self._initify()
        if self.border:
            self._bordify()
        self._textify()


    def draw(self, canvas: pygame.Surface) -> None:
        """ draw the sprite image on the given surface """
        canvas.blit(self.image, self.rect)


    @property
    def text(self) -> str:
        """ the text to display on `image` """
        return self._text
    @text.setter
    def text(self, text: str) -> None:
        """ the text to display on `image` """
        if not isinstance(text, str):
            raise TypeError(
                "The property `text` must be a string."
                )
        self._text = text


    @property
    def text_color(self) -> pygame.Color:
        """ the color of the text to display """
        return getattr(
            self, "_text_color", SpritesDefaults.TEXT_COLOR
            )
    @text_color.setter
    def text_color(self, color: pygame.Color) -> None:
        """ the color of the text to display """
        if not isinstance(color, pygame.Color):
            raise TypeError(
                "The property `text_color` must be a "
                "pygame.Color object."
                )
        self._text_color = color


    @property
    def border(self) -> bool:
        """ whether or not to draw a border """
        return getattr(
            self, "_border", SpritesDefaults.BORDER
            )
    @border.setter
    def border(self, border: bool) -> None:
        """ whether or not to draw a border """
        if not isinstance(border, bool):
            raise TypeError(
                "The property `border` must be boolean."
                )
        self._border = border


    @property
    def text_buffer(self) -> float:
        """
        a positive float at most 1 that scales text
        to add space as a buffer
        """
        return getattr(
            self,
            "_text_buffer",
            SpritesDefaults.TEXT_BUFFER
            )
    @text_buffer.setter
    def text_buffer(self, text_buffer: float) -> None:
        """
        a positive float at most 1 that scales text
        to add space as a buffer
        """
        if not isinstance(text_buffer, float):
            raise TypeError(
                "The property `text_buffer` must be a "
                "float satisfying `0 < text_buffer <= 1`."
                )
        self._text_buffer = text_buffer


    @property
    def color_key(self) -> pygame.Color | None:
        """ the color set to be transparent """
        return getattr(
            self, "_color_key", SpritesDefaults.COLOR_KEY
            )
    @color_key.setter
    def color_key(self, color: pygame.Color | None) -> None:
        """ the color set to be transparent """
        if not isinstance(color, pygame.Color):
            raise TypeError(
                "The property `color_key` must be a "
                "pygame.Color object."
                )
        self._color_key = color


    @property
    def border_color(self) -> pygame.Color:
        """ the color of the border, if drawn """
        return getattr(
            self,
            "_border_color",
            SpritesDefaults.BORDER_COLOR
            )
    @border_color.setter
    def border_color(self, color: pygame.Color) -> None:
        """ the color of the border, if drawn """
        if not isinstance(color, pygame.Color):
            raise TypeError(
                "The property `border_color` must be a "
                "pygame.Color object."
                )
        self._border_color = color


    @property
    def rounding_ratio(self) -> float:
        """
        the ratio of size to corner radius as a
        nonnegative float no more than 1
        """
        return getattr(
            self,
            "_rounding_ratio",
            SpritesDefaults.ROUNDING_RATIO
            )
    @rounding_ratio.setter
    def rounding_ratio(self, rounding_ratio: float) -> None:
        """
        the ratio of size to corner radius as a
        nonnegative float no more than 1
        """
        if not isinstance(rounding_ratio, float):
            raise TypeError(
                "The property `rounding_ratio` must be a "
                "float satisfying "
                "`0 <= rounding_ratio <= 1`."
                )
        if not 0 <= rounding_ratio <= 1:
            raise ValueError(
                "The property `rounding_ratio` must be a "
                "float satisfying "
                "`0 <= rounding_ratio <= 1`."
                )
        self._rounding_ratio = rounding_ratio


    @property
    def line_width(self) -> int:
        """
        the line width when drawing as a positive integer
        """
        return getattr(
            self,
            "_line_width",
            SpritesDefaults.LINE_WIDTH
            )
    @line_width.setter
    def line_width(self, line_width: int) -> None:
        """
        the line width when drawing as a positive integer
        """
        if not isinstance(line_width, int):
            raise TypeError(
                "The property `line_width` must be a "
                "positive integer."
                )
        if line_width <= 0:
            raise ValueError(
                "The property `line_width` must be a "
                "positive integer."
                )
        self._line_width = line_width


class Letter(Text):
    """
    class for all letter elements in the strands game

    Attributes:
        image (pygame.Surface)
        rect (pygame.Rect)
        text (str)
        text_color (pygame.Color)
        border (bool)
        text_buffer (float)
        color_key (pygame.Color | None)
        border_color (pygame.Color)
        line_width (int)
        highlight1 (pygame.Color | None)
        highlight2 (pygame.Color | None)
        position (PosBase)
    """

    # image: pygame.Surface
    # rect: pygame.Rect
    # _text: str
    # _text_color: pygame.Color
    # _border: bool
    # _text_buffer: float
    # _color_key: pygame.Color
    # _border_color: pygame.Color
    # _line_width: int
    _highlight1: pygame.Color | None
    _highlight2: pygame.Color | None
    _position: PosBase


    def __init__(
        self, pos: PosBase, ch: str, specs: Specs
        ) -> None:
        """
        constructor

        Inputs:
            pos (PosBase): the position on the board
            ch (str): the letter to display
            specs (Specs): the x center, y center, width,
                and height defining the containing
                rectangle
        """
        super().__init__(ch, specs)
        self.position = pos


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
        def check(var: str, val: Any) -> tuple[int, int]:
            """
            helper function to verify values

            Inputs:
                var (str): the string name of the
                    variable being checked
                val (Any): the value to verify
            """
            assert (
                isinstance(var, str)
                and var in ["offset", "spacing", "size"]
                ), (
                "The argument `var` must be a string "
                "corresponding to the variable being "
                "checked."
                )
            if (
                isinstance(val, tuple)
                and len(val) == 2
                and all(isinstance(n, int) for n in val)
                ):
                pass
            elif isinstance(val, int):
                val = (val, val)
            else:
                raise ValueError(
                    f"The argument `{var}` must be an "
                    "integer or a tuple of two integers."
                    )
            return val
        xb, yb = check("offset", offset)
        sx, sy = check("spacing", spacing)
        w, h = check("size", size)
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
            pygame.draw.ellipse(
                self.image,
                highlight,
                self.image.get_rect()
                )


    def _bordify(self) -> None:
        """ draw a circular border """
        pygame.draw.ellipse(
            self.image,
            self.border_color,
            self.image.get_rect(),
            self.line_width
            )


    def render(self) -> None:
        """ render the image """
        self._initify()
        self._highlightify()
        if self.border:
            self._bordify()
        self._textify()


    @property
    def highlight1(self) -> pygame.Color | None:
        """
        the primary highlight color, or None to default
        to the secondary highlight color, `highlight2`
        """
        return getattr(
            self, "_highlight1", SpritesDefaults.HIGHLIGHT1
            )
    @highlight1.setter
    def highlight1(
        self,
        color: pygame.Color | None
        ) -> None:
        """
        the primary highlight color, or None to default
        to the secondary highlight color, `highlight2`
        """
        if (
            color is not None
            and not isinstance(color, pygame.Color)
            ):
            raise TypeError(
                "The property `highlight1` must be a "
                "pygame.Color object or None."
                )
        self._highlight1 = color


    @property
    def highlight2(self) -> pygame.Color | None:
        """
        the secondary highlight color, only used if
        the primary highlight color, `highlight2`,
        is None, or None to default to no highlight
        """
        return getattr(
            self, "_highlight2", SpritesDefaults.HIGHLIGHT2
            )
    @highlight2.setter
    def highlight2(
        self,
        color: pygame.Color | None
        ) -> None:
        """
        the secondary highlight color, only used if
        the primary highlight color, `highlight2`,
        is None, or None to default to no highlight
        """
        if (
            color is not None
            and not isinstance(color, pygame.Color)
            ):
            raise TypeError(
                "The property `highlight2` must be a "
                "pygame.Color object or None."
                )
        self._highlight2 = color


    @property
    def text(self) -> str:
        """
        a single character of text to display on `image`
        """
        return self._text
    @text.setter
    def text(self, text: str) -> None:
        """
        a single character of text to display on `image`
        """
        if not isinstance(text, str):
            raise TypeError(
                "The property `text` must be a single "
                "character string."
                )
        if len(text) > 1:
            raise ValueError(
                "The property `text` must be a single "
                "character string."
                )
        self._text = text


    @property
    def position(self) -> PosBase:
        """ the position of the letter on the game board """
        return self._position
    @position.setter
    def position(self, position: PosBase) -> None:
        if not isinstance(position, PosBase):
            raise ValueError(
                "The property `position` must be a "
                "PosBase object."
                )
        self._position = position


class Meter(Text):
    """
    class for a meter element in the game

    Attributes:
        image (pygame.Surface)
        rect (pygame.Rect)
        text (str)
        text_color (pygame.Color)
        border (bool)
        text_buffer (float)
        color_key (pygame.Color | None)
        border_color (pygame.Color)
        rounding_ratio (float)
        line_width (int)
        textform (str | None)
        meter (int)
        threshold (int)
        use_bar (bool)
        fill_color (pygame.Color)
    """

    # image: pygame.Surface
    # rect: pygame.Rect
    # _text: str
    # _text_color: pygame.Color
    # _border: bool
    # _text_buffer: float
    # _color_key: pygame.Color
    # _border_color: pygame.Color
    # _rounding_ratio: float
    # _line_width: int
    _textform: str | None
    _meter: int
    _threshold: int
    _use_bar: bool
    _fill_color: pygame.Color


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
            text (str): the text to display, optionally
                including the formatting parameters
                'meter' and 'threshold' to update the
                text with the current progress
            specs (Specs): the x center, y center, width,
                and height defining the containing
                rectangle
            threshold (int): a positive integer
                representing the meter threshold
            use_bar (bool): whether or not to show a
                loading bar
        """
        super().__init__(text, specs)
        self.use_bar = use_bar
        self.threshold = threshold
        try:
            self.textform = text
        except ValueError:
            pass
        self.remeter(0)


    def remeter(self, meter: int) -> None:
        """
        update the meter

        If the argument `meter` is greater than
        `threshold`, then `meter` is updated to match
        the `threshold`. If the argument `meter` is
        less than 0, then `meter` is updated to be 0.
        """
        self.meter = max(min(meter, self.threshold), 0)
        if self.textform is not None:
            self.text = self.textform.format(
                meter = self.meter,
                threshold = self.threshold
                )


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
        border_radius = round(
            self.rounding_ratio * min(rect.size)
            )
        if self.meter == self.threshold:
            pygame.draw.rect(
                self.image,
                self.fill_color,
                fill,
                border_radius = border_radius
                )
        else:
            pygame.draw.rect(
                self.image,
                self.fill_color,
                fill,
                border_top_left_radius = border_radius,
                border_bottom_left_radius = border_radius
                )
        self._bordify()


    @property
    def textform(self) -> str | None:
        """
        a string with the formatting parameters 'meter'
        and 'threshold' used to update `text` with the
        current meter value, or None if `text` is not used
        to display the current meter values
        """
        return getattr(
            self, "_textform", SpritesDefaults.TEXTFORM
            )
    @textform.setter
    def textform(self, textform: str) -> None:
        """
        a string with the formatting parameters 'meter'
        and 'threshold' used to update `text` with the
        current meter value, or None if `text` is not used
        to display the current meter values
        """
        if not isinstance(textform, str):
            raise TypeError(
                "The property `textform` must be a "
                "string with the parameters `meter` and "
                "`threshold` or None."
                )
        parameters = set(
            field for _, field, _, _
            in Formatter().parse(textform)
            )
        if parameters == {'meter', 'threshold'}:
            self._textform = textform
        else:
            raise ValueError(
                "The property `textform` must be a "
                "string with the parameters `meter` and "
                "`threshold` or None."
                )


    @property
    def meter(self) -> int:
        """
        the meter value as a nonnegative integer no more
        than `threshold`
        """
        return getattr(
            self, "_meter", SpritesDefaults.METER
            )
    @meter.setter
    def meter(self, meter: int) -> None:
        """
        the meter value as a nonnegative integer no more
        than `threshold`
        """
        if not isinstance(meter, int):
            raise TypeError(
                "The property `meter` must be a "
                "nonnegative integer no more than "
                "the property `threshold`."
                )
        if meter < 0 or meter > self.threshold:
            raise ValueError(
                "The property `meter` must be a "
                "nonnegative integer no more than "
                "the property `threshold`."
                )
        self._meter = meter


    @property
    def threshold(self) -> int:
        """ a positive integer threshold """
        return self._threshold
    @threshold.setter
    def threshold(self, threshold: int) -> None:
        """ a positive integer threshold """
        if not isinstance(threshold, int):
            raise TypeError(
                "The property `threshold` must be a "
                "positive integer no less than meter."
                )
        if threshold <= 0 or self.meter > threshold:
            raise ValueError(
                "The property `threshold` must be a "
                "positive integer no less than meter."
                )
        self._threshold = threshold


    @property
    def use_bar(self) -> bool:
        """
        whether or not to show the current meter
        value as a loading bar
        """
        return self._use_bar
    @use_bar.setter
    def use_bar(self, use_bar: bool) -> None:
        if not isinstance(use_bar, bool):
            raise TypeError(
                "The property `use_bar` must be boolean."
                )
        self._use_bar = use_bar


    @property
    def fill_color(self) -> pygame.Color:
        """ the color to fill the loading bar with """
        return getattr(
            self, "_fill_color", SpritesDefaults.FILL_COLOR
            )
    @fill_color.setter
    def fill_color(self, color: pygame.Color) -> None:
        """ the color to fill the loading bar with """
        if not isinstance(color, pygame.Color):
            raise TypeError(
                "The property `fill_color` must be a "
                "pygame.Color object."
                )
        self._fill_color = color
