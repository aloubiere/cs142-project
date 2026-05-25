""" Containers for the Sprites """

from abc import abstractmethod
import pygame


class ContainerBaseDefaults:
    """ class for ContainerBase defaults """
    BORDER: bool = False
    BORDER_COLOR: pygame.Color = pygame.Color("black")
    BORDER_WIDTH: int = 2
    FILL: bool = False
    FILL_COLOR: pygame.Color = pygame.Color("white")
    RECT: pygame.Rect | None = None


class ContainerBase:
    """
    a class for storing container related parameters
    """

    _border: bool
    _border_color: pygame.Color
    _border_width: int
    _fill: bool
    _fill_color: pygame.Color

    DEFAULTS = ContainerBaseDefaults()


    def __init__(self) -> None:
        """ constructor """
        self.border = self.DEFAULTS.BORDER
        self.border_color = self.DEFAULTS.BORDER_COLOR
        self.border_width = self.DEFAULTS.BORDER_WIDTH
        self.fill = self.DEFAULTS.FILL
        self.fill_color = self.DEFAULTS.FILL_COLOR


    def _check_draw(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None
        ) -> tuple[pygame.Surface, pygame.Rect]:
        """ type check and prepare for drawing """
        if not isinstance(image, pygame.Surface):
            raise TypeError(
                "The argument `image` must be a "
                "pygame.Surface object. The type is "
                f"{type(image)}."
                )
        if rect is None:
            rect = image.get_rect()
        elif not isinstance(rect, pygame.Rect):
            raise TypeError(
                "The argument `rect` must be a "
                "pygame.Rect object or None. The type is "
                f"{type(rect)}."
                )
        return image, rect


    def draw(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = DEFAULTS.RECT
        ) -> None:
        """
        draw a container on the given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn container, or None to
                default to the image rect
        """
        self.draw_fill(image, rect)
        self.draw_border(image, rect)


    @abstractmethod
    def draw_fill(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = DEFAULTS.RECT
        ) -> None:
        """
        fill a rectangular container on the given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn border, or None to
                default to the image rect
        """


    @abstractmethod
    def draw_border(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = DEFAULTS.RECT
        ) -> None:
        """
        border a rectangular container on the given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn border, or None to
                default to the image rect
        """


    @property
    def border(self) -> bool:
        """ whether or not to border the container """
        return self._border
    @border.setter
    def border(self, border: bool) -> None:
        """ whether or not to border the container """
        if not isinstance(border, bool):
            raise TypeError(
                "The property `border` must be boolean. "
                f"The type is {type(border)}."
                )
        self._border = border


    @property
    def fill(self) -> bool:
        """ whether or not to fill the container """
        return self._fill
    @fill.setter
    def fill(self, fill: bool) -> None:
        """ whether or not to fill the container """
        if not isinstance(fill, bool):
            raise TypeError(
                "The property `fill` must be boolean. "
                f"The type is {type(fill)}."
                )
        self._fill = fill


    @property
    def border_color(self) -> pygame.Color:
        """ the border color of the container """
        return self._border_color
    @border_color.setter
    def border_color(
        self,
        border_color: pygame.Color
        ) -> None:
        """ the border color of the container """
        if not isinstance(border_color, pygame.Color):
            raise TypeError(
                "The property `border_color` must be a "
                "pygame.Color object. The type is "
                f"{type(border_color)}."
                )
        self._border_color = border_color


    @property
    def fill_color(self) -> pygame.Color:
        """ the fill color of the container """
        return self._fill_color
    @fill_color.setter
    def fill_color(
        self,
        fill_color: pygame.Color
        ) -> None:
        """ the fill color of the container """
        if not isinstance(fill_color, pygame.Color):
            raise TypeError(
                "The property `fill_color` must be a "
                "pygame.Color object. The type is "
                f"{type(fill_color)}."
                )
        self._fill_color = fill_color


    @property
    def border_width(self) -> int:
        """
        the border width when drawing as a positive integer
        """
        return self._border_width
    @border_width.setter
    def border_width(self, border_width: int) -> None:
        """
        the border width when drawing as a positive integer
        """
        if not isinstance(border_width, int):
            raise TypeError(
                "The property `border_width` must be a "
                "positive integer. The type is "
                f"{type(border_width)}."
                )
        if border_width <= 0:
            raise ValueError(
                "The property `border_width` must be a "
                "positive integer. The value is "
                f"{border_width}."
                )
        self._border_width = border_width


class RectContainerDefaults(ContainerBaseDefaults):
    """ class for RectContainer defaults """
    # same as ContainerBase


class RectContainer(ContainerBase):
    """
    a class for storing rectangular container related
    parameters
    """

    # _border: bool
    # _border_color: pygame.Color
    # _border_width: int
    # _fill: bool
    # _fill_color: pygame.Color

    DEFAULTS = RectContainerDefaults()


    def draw_fill(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = DEFAULTS.RECT
        ) -> None:
        """
        fill a rectangular container on the given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn fill, or None to
                default to the image rect
        """
        image, rect = self._check_draw(image, rect)
        if self.fill:
            pygame.draw.rect(
                image,
                self.fill_color,
                rect
                )


    def draw_border(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = DEFAULTS.RECT
        ) -> None:
        """
        border a rectangular container on the given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn border, or None to
                default to the image rect
        """
        image, rect = self._check_draw(image, rect)
        if self.border:
            pygame.draw.rect(
                image,
                self.border_color,
                rect,
                self.border_width
                )


class RoundedContainerDefaults(ContainerBaseDefaults):
    """ class for RoundedContainer defaults """
    ROUNDING_RATIO = 1/12


class RoundedContainer(ContainerBase):
    """
    a class for storing rounded container related parameters
    """

    # _border: bool
    # _border_color: pygame.Color
    # _border_width: int
    # _fill: bool
    # _fill_color: pygame.Color
    _rounding_ratio: float

    DEFAULTS = RoundedContainerDefaults()


    def __init__(self) -> None:
        """ constructor """
        super().__init__()
        self.rounding_ratio = self.DEFAULTS.ROUNDING_RATIO


    def draw_fill(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = DEFAULTS.RECT
        ) -> None:
        """
        fill a rounded rectangular container on the
        given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn fill, or None to
                default to the image rect
        """
        image, rect = self._check_draw(image, rect)
        if self.fill:
            pygame.draw.rect(
                image,
                self.fill_color,
                rect,
                round(self.rounding_ratio * min(rect.size))
                )


    def draw_border(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = DEFAULTS.RECT
        ) -> None:
        """
        border a rounded rectangular container on the
        given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn border, or None to
                default to the image rect
        """
        image, rect = self._check_draw(image, rect)
        if self.border:
            pygame.draw.rect(
                image,
                self.border_color,
                rect,
                self.border_width,
                round(self.rounding_ratio * min(rect.size))
                )


    @property
    def rounding_ratio(self) -> float:
        """
        the ratio of size to corner radius as a
        nonnegative float no more than 1
        """
        return self._rounding_ratio
    @rounding_ratio.setter
    def rounding_ratio(
        self,
        rounding_ratio: float
        ) -> None:
        """
        the ratio of size to corner radius as a
        nonnegative float no more than 1
        """
        if not isinstance(rounding_ratio, float):
            raise TypeError(
                "The property `rounding_ratio` must be a "
                "float satisfying "
                "`0 <= rounding_ratio <= 1`. The type is "
                f"{type(rounding_ratio)}."
                )
        if not 0 <= rounding_ratio <= 1:
            raise ValueError(
                "The property `rounding_ratio` must be a "
                "float satisfying "
                "`0 <= rounding_ratio <= 1`. The value is "
                f"{rounding_ratio}."
                )
        self._rounding_ratio = rounding_ratio


class CircularContainerDefaults(ContainerBaseDefaults):
    """ class for CircularContainer defaults """
    # same as ContainerBase for now


class CircularContainer(ContainerBase):
    """
    a class for storing circular container related parameters
    """

    # _border: bool
    # _border_color: pygame.Color
    # _border_width: int
    # _fill: bool
    # _fill_color: pygame.Color


    def draw_fill(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = None
        ) -> None:
        """
        fill a circular container on the given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn fill, or None to
                default to the image rect
        """
        image, rect = self._check_draw(image, rect)
        if self.fill:
            pygame.draw.ellipse(
                image,
                self.fill_color,
                rect
                )


    def draw_border(
        self,
        image: pygame.Surface,
        rect: pygame.Rect | None = None
        ) -> None:
        """
        border a circular container on the given image

        Inputs:
            image (pygame.Surface): the image to draw on
            rect (pygame.Rect | None): a rect to size and
                position the drawn border, or None to
                default to the image rect
        """
        image, rect = self._check_draw(image, rect)
        if self.border:
            pygame.draw.ellipse(
                image,
                self.border_color,
                rect,
                self.border_width
                )
