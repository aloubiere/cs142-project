""" Sprites for the GUI """

from typing import NamedTuple, Any
from string import Formatter
import pygame
from gui_files.container import (
    ContainerBase, RectContainer,
    RoundedContainer, CircularContainer
    )
from gui_files.text import Text


class GridSpecsBase(NamedTuple):
    """
    (offset, spacing, size)
    ((xb, yb), (sx, sy), (w, h))
    """
    # the x and y offsets as a tuple
    offset: tuple[int, int]

    # the x and y spacings as a tuple
    spacing: tuple[int, int]

    # the width and height as a tuple
    size: tuple[int, int]


class GridSpecs(GridSpecsBase):
    """
    (offset, spacing, size)
    ((xb, yb), (sx, sy), (w, h))
    """
    def __new__(
        cls,
        offset: int | tuple[int, int],
        spacing: int | tuple[int, int],
        size: int | tuple[int, int]
        ) -> "GridSpecs":
        """
        verify values first and allow for broadcasting of
        one integer to a tuple of ints
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
            if isinstance(val, tuple):
                if len(val) != 2:
                    raise TypeError(
                        f"The argument `{var}` must be an "
                        "integer or a tuple of two "
                        "integers. The argument is a "
                        "tuple but the length is "
                        f"{len(val)}."
                        )
                if any(not isinstance(n, int) for n in val):
                    raise TypeError(
                        f"The argument `{var}` must be an "
                        "integer or a tuple of two "
                        "integers. The argument is a "
                        "tuple of length 2 but the item "
                        "types are "
                        f"{(type(n) for n in val)}."
                        )
            elif isinstance(val, int):
                val = (val, val)
            else:
                raise TypeError(
                    f"The argument `{var}` must be an "
                    "integer or a tuple of two integers. "
                    f"The type is {type(val)}."
                    )
            return val
        xb, yb = check("offset", offset)
        sx, sy = check("spacing", spacing)
        w, h = check("size", size)
        return super().__new__(
            cls, (xb, yb), (sx, sy), (w, h)
            )


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
                    "nonnegative integer. The type is "
                    f"{type(val)}."
                    )
            if val < 0:
                raise ValueError(
                    f"The attribute `{var}` must be a "
                    "nonnegative integer. The value is "
                    f"{val}."
                    )
        check("x", x)
        check("y", y)
        check("w", w)
        check("h", h)
        return super().__new__(cls, x, y, w, h)


class TextSpriteDefaults:
    """ class for TextSprite defaults """
    CONTAINER: type[ContainerBase] = RoundedContainer
    COLOR_KEY: pygame.Color | None = pygame.Color("white")


class TextSprite(pygame.sprite.Sprite):
    """
    class for all text elements in the game
    """

    image: pygame.Surface
    rect: pygame.Rect
    texts: list[Text]
    containers: list[ContainerBase]
    _color_key: pygame.Color | None

    DEFAULTS = TextSpriteDefaults()


    def __init__(
        self,
        text: str,
        specs: Specs
        ) -> None:
        """
        constructor

        Inputs:
            text (str): the text to display
            specs (Specs): the x position, y position,
                width, and height as a Specs object
        """
        super().__init__()
        self.texts = [Text(text)]
        self.containers = [self.DEFAULTS.CONTAINER()]
        self.resize(specs)
        self.color_key = self.DEFAULTS.COLOR_KEY


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
                f"object. The type is {type(specs)}."
                )
        self.rect = pygame.Rect(0, 0, specs.w, specs.h)
        self.rect.center = (specs.x, specs.y)


    def _initify(self) -> None:
        """ initialize the image surface """
        self.image = pygame.Surface(
            self.rect.size,
            pygame.SRCALPHA
            )
        if self.color_key is not None:
            self.image.fill(self.color_key)
        self.image.set_colorkey(self.color_key)


    def _textify(self) -> None:
        """ draw the text """
        self.text.draw(self.image)


    def _containify(self) -> None:
        """ draw the container """
        self.container.draw(self.image)


    def render(self) -> None:
        """ render the image """
        self._initify()
        self._containify()
        self._textify()


    def draw(self, canvas: pygame.Surface) -> None:
        """ draw the sprite image on the given surface """
        try:
            canvas.blit(self.image, self.rect)
        except AttributeError as exc:
            raise AttributeError(
                "Please render the image first."
                ) from exc


    @property
    def color_key(self) -> pygame.Color | None:
        """ the color set to be transparent """
        return self._color_key
    @color_key.setter
    def color_key(
        self,
        color: pygame.Color | None
        ) -> None:
        """ the color set to be transparent """
        if not isinstance(color, pygame.Color):
            raise TypeError(
                "The property `color_key` must be a "
                "pygame.Color object. The type is "
                f"{type(color)}."
                )
        self._color_key = color


    def text_override(
        self,
        index: int = 0
        ) -> None:
        """ clear `texts` except for the given index """
        self.texts = self.texts[index:index+1]


    def container_override(
        self,
        index: int = 0
        ) -> None:
        """
        clear `containers` except for the given index
        """
        self.containers = self.containers[index:index+1]


    @property
    def text(self) -> Text:
        """ the currently used text """
        try:
            return self.texts[-1]
        except IndexError as exc:
            raise AttributeError(
                "No property `text` found."
                ) from exc
    @text.setter
    def text(self, text: Text) -> None:
        """
        the currently used text

        Note: reassigning this does not delete the
        previously used text.
        """
        if not isinstance(text, Text):
            raise TypeError(
                "The property `text` must be a Text "
                f"object. The type is {type(text)}."
                )
        self.texts.append(text)
    @text.deleter
    def text(self) -> None:
        """ the currently used text """
        del self.texts[-1]


    @property
    def container(self) -> ContainerBase:
        """ the currently used container """
        try:
            return self.containers[-1]
        except IndexError as exc:
            raise AttributeError(
                "No property `container` found."
                ) from exc
    @container.setter
    def container(self, container: ContainerBase) -> None:
        """
        the currently used container

        Note: reassigning this does not delete the
        previously used container.
        """
        if not isinstance(container, ContainerBase):
            raise TypeError(
                "The property `container` must be a "
                "ContainerBase object. The type is "
                f"{type(container)}."
                )
        self.containers.append(container)
    @container.deleter
    def container(self) -> None:
        """ the currently used container """
        del self.containers[-1]


class LetterSpriteDefaults(TextSpriteDefaults):
    """ class for LetterSprite defaults """
    CONTAINER: type[ContainerBase] = CircularContainer


class LetterSprite(TextSprite):
    """
    class for all letter elements in the strands game
    """

    # image: pygame.Surface
    # rect: pygame.Rect
    # texts: list[Text]
    # containers: list[ContainerBase]
    # _color_key: pygame.Color | None
    _position: tuple[int, int]

    DEFAULTS = LetterSpriteDefaults()


    def __init__(
        self,
        pos: tuple[int, int],
        ch: str,
        specs: Specs | GridSpecs
        ) -> None:
        """
        constructor

        Inputs:
            pos (tuple[int, int]): a position on a grid
            ch (str): the letter to display
            specs (Specs | GridSpecs): either a Specs
                object indicating the x position, y
                position, width, and height, or a
                GridSpecs object indicating the offset,
                spacing, and size which are then used
                with the `position` attribute to
                calculate the position and size
        """
        self.position = pos
        super().__init__(ch, self._grid_to_specs(specs))


    def _grid_to_specs(
        self,
        specs: GridSpecs | Specs
        ) -> Specs:
        """
        converts GridSpecs to Specs if needed
        """
        if isinstance(specs, GridSpecs):
            r, c = self._position
            (xb, yb), (sx, sy), (w, h) = specs
            specs = Specs(
                round(xb + (c + 1/2) * sx),
                round(yb + (r + 1/2) * sy),
                w, h
                )
        elif not isinstance(specs, Specs):
            raise TypeError(
                "The argument `specs` must be either a "
                "Specs or GridSpecs object. The type is "
                f"{type(specs)}."
                )
        return specs


    def resize(self, specs: Specs | GridSpecs) -> None:
        """
        update the size and/or position of the rectangle
        containing the text

        Inputs:
            specs (Specs | GridSpecs): either a Specs
                object indicating the position and size
                or a GridSpecs object indicating the
                offset, spacing, and size which are then
                used with the `position` attribute to
                calculate the position and size
        """
        super().resize(self._grid_to_specs(specs))


    @property
    def position(self) -> tuple[int, int]:
        """ the position of the letter on a grid """
        return self._position
    @position.setter
    def position(self, position: tuple[int, int]) -> None:
        if isinstance(position, tuple):
            if len(position) != 2:
                raise TypeError(
                    f"The property `position` must be a "
                    "tuple of two integers. The given "
                    "value is a tuple but the length is "
                    f"{len(position)}."
                    )
            if any(
                not isinstance(n, int) for n in position
                ):
                raise TypeError(
                    f"The property `position` must be a "
                    "tuple of two integers. The given "
                    "value is a tuple of length 2 but the "
                    "item types are "
                    f"{(type(n) for n in position)}."
                    )
            self._position = position
            return
        raise TypeError(
            f"The property `position` must be a tuple of "
            "two integers. The given value has type "
            f"{type(position)}."
            )


class MeterSpriteDefaults(TextSpriteDefaults):
    """ class for MeterSprite defaults """
    METER = 0
    BAR_COLOR: pygame.Color = pygame.Color("gray")


class MeterSprite(TextSprite):
    """
    class for a meter element in the game
    """

    # image: pygame.Surface
    # rect: pygame.Rect
    # texts: list[Text]
    # containers: list[ContainerBase]
    # _color_key: pygame.Color | None
    _textform: str | None
    _meter: int
    _threshold: int
    _use_bar: bool
    _bar_color: pygame.Color

    DEFAULTS = MeterSpriteDefaults()


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
            text (str): the text to display,
                optionally including the formatting
                parameters 'meter' and 'threshold' to
                update the text with the current progress
            specs (Specs): the x position, y position,
                width, and height as a Specs object
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
            self.textform = None
        self.remeter(self.DEFAULTS.METER)
        self.bar_color = self.DEFAULTS.BAR_COLOR


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
            self.text = Text(self.textform.format(
                meter = self.meter,
                threshold = self.threshold
                ))


    def render(self) -> None:
        """ render the image """
        self._initify()
        if self._use_bar:
            self._barify()
        else:
            self._containify()
        self._textify()


    def _barify(self) -> None:
        """ create a progress bar """
        rect = self.image.get_rect()
        fill = rect.scale_by(
            self.meter / self.threshold, 1
            )
        fill.topleft = (0, 0)
        if isinstance(self.container, RoundedContainer):
            border_radius = round(
                self.container.rounding_ratio
                * min(rect.size)
                )
        elif isinstance(self.container, RectContainer):
            border_radius = 0
        else:
            raise NotImplementedError
        if self.meter == self.threshold:
            pygame.draw.rect(
                self.image,
                self.bar_color,
                fill,
                border_radius = border_radius
                )
        else:
            pygame.draw.rect(
                self.image,
                self.bar_color,
                fill,
                border_top_left_radius = border_radius,
                border_bottom_left_radius = border_radius
                )
        self._containify()


    @property
    def textform(self) -> str | None:
        """
        a string with the formatting parameters 'meter'
        and 'threshold' used to update `text` with the
        current meter value, or None if `text` is not used
        to display the current meter values
        """
        return self._textform
    @textform.setter
    def textform(self, textform: str | None) -> None:
        """
        a string with the formatting parameters 'meter'
        and 'threshold' used to update `text` with the
        current meter value, or None if `text` is not used
        to display the current meter values
        """
        if textform is None:
            self._textform = textform
            return
        elif not isinstance(textform, str):
            raise TypeError(
                "The property `textform` must be a "
                "string with the parameters `meter` and "
                "`threshold` or None. The type is "
                f"{type(textform)}."
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
                "`threshold` or None. The parameters are "
                f"{parameters}."
                )


    @property
    def meter(self) -> int:
        """
        the meter value as a nonnegative integer no more
        than `threshold`
        """
        return getattr(self, "_meter", self.DEFAULTS.METER)
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
                "the property `threshold`. The type is "
                f"{type(meter)}."
                )
        if meter < 0 or meter > self.threshold:
            raise ValueError(
                "The property `meter` must be a "
                "nonnegative integer no more than "
                "the property `threshold`. The value is "
                f"{meter} and the value of `threshold` "
                f"is {self.threshold}."
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
                "positive integer no less than meter. "
                f"The type is {type(threshold)}."
                )
        if threshold <= 0 or self.meter > threshold:
            raise ValueError(
                "The property `threshold` must be a "
                "positive integer no less than meter. "
                f"The value is {threshold} and the value "
                f"of `meter` is {self.meter}."
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
                "The property `use_bar` must be boolean. "
                f"The type is {type(use_bar)}."
                )
        self._use_bar = use_bar


    @property
    def bar_color(self) -> pygame.Color:
        """ the color to fill the loading bar with """
        return self._bar_color
    @bar_color.setter
    def bar_color(self, color: pygame.Color) -> None:
        """ the color to fill the loading bar with """
        if not isinstance(color, pygame.Color):
            raise TypeError(
                "The property `bar_color` must be a "
                "pygame.Color object. The type is "
                f"{type(color)}."
                )
        self._bar_color = color
