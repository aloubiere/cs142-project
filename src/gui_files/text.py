""" Text for the Sprites """
import pygame


class TextDefaults:
    """ class for Text object defaults """
    TEXT: str = ""
    COLOR: pygame.Color = pygame.Color("black")
    BUFFER: float = 1


class Text:
    """ a class for storing text related parameters """

    _text: str
    _color: pygame.Color
    _buffer: float

    DEFAULTS = TextDefaults()

    def __init__(
        self,
        text: str = DEFAULTS.TEXT,
        color: pygame.Color = DEFAULTS.COLOR,
        buffer: float = DEFAULTS.BUFFER
        ) -> None:
        """ constructor """
        self.text = text
        self.color = color
        self.buffer = buffer


    def draw(self, image: pygame.Surface) -> None:
        """ draw the text onto the given image """
        rect = image.get_rect()
        size = height = round(rect.height * self.buffer)
        width = round(rect.width * self.buffer)
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
        width, height = tuple(rect.size)
        image.blit(
            text,
            ((width - w) / 2, (height - h) / 2)
            )


    @property
    def text(self) -> str:
        """ the text to display """
        return self._text
    @text.setter
    def text(self, text: str) -> None:
        """ the text to display """
        if not isinstance(text, str):
            raise TypeError(
                "The property `text` must be a string. "
                f"The type is {type(text)}."
                )
        self._text = text


    @property
    def color(self) -> pygame.Color:
        """ the color of the text to display """
        return self._color
    @color.setter
    def color(self, color: pygame.Color) -> None:
        """ the color of the text to display """
        if not isinstance(color, pygame.Color):
            raise TypeError(
                "The property `color` must be a "
                "pygame.Color object. The type is "
                f"{type(color)}."
                )
        self._color = color


    @property
    def buffer(self) -> float:
        """
        a positive float at most 1 that scales text
        to add space as a buffer
        """
        return self._buffer
    @buffer.setter
    def buffer(self, buffer: float) -> None:
        """
        a positive float or int at most 1 that scales text
        to add space as a buffer
        """
        if not isinstance(buffer, (float, int)):
            raise TypeError(
                "The property `buffer` must be a float or "
                "int satisfying `0 < text_buffer <= 1`. "
                f"The type is {type(buffer)}."
                )
        if not 0 < buffer <= 1:
            raise ValueError(
                "The property `buffer` must be a float or "
                "int satisfying `0 < buffer <= 1`. "
                f"The value is {buffer}"
                )
        self._buffer = buffer
