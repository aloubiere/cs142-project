"""
Strands GUI Implementation
"""
# Amber

import sys
from typing import TypeAlias, Callable, Any
from functools import wraps
import pygame
from base import (
    PosBase, StrandBase, StrandsGameBase
    )
from strands import Pos, StrandsGame

FRAME_RATE: int = 24
BUFFER: int = 25
CANVAS_COLOR: pygame.Color = pygame.Color("white")
CANVAS_SIZE: tuple[int, int] = (600, 600)
CAPTION = "Strands"

GRID_SIZE: int = 60
HEADER = FOOTER = 50
TEXT_BUFFER: float = 1/6
LETTER_COLOR: pygame.Color = pygame.Color("black")
SELECT_COLOR: pygame.Color = pygame.Color("lightgray")
HINT_COLOR: pygame.Color = pygame.Color("lightblue")
FOUND_COLOR: pygame.Color = pygame.Color("lightblue")
TEXT_COLOR: pygame.Color = pygame.Color("black")


Specs: TypeAlias = tuple[int, int, int, int]

class Text(pygame.sprite.Sprite):
    """ class for all text elements in the game """

    image: pygame.Surface
    rect: pygame.Rect
    text: str
    color: pygame.Color

    def __init__(self, text: str, xywh: Specs) -> None:
        """ constructor """
        # TODO


    def resize(self, xywh: Specs) -> None:
        """ update the size and/or position """
        # TODO


    def retext(
        self,
        text: str,
        color: pygame.Color | None = None
        ) -> None:
        """ update the text """
        # TODO


    def render(self) -> None:
        """ update the image """
        # TODO


class Letter(Text):
    """ class for all letter elements in the game """

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
        assert isinstance(pos, PosBase), \
            "The argument `pos` must be a PosBase object."
        self.position = pos
        super().__init__(ch, xywh)


    def update(
        self,
        xb: int,
        yb: int,
        w: int,
        h: int
        ) -> None:
        """ update the size and/or position """
        self.resize((
            xb + self.position.c * w,
            yb + self.position.r * h,
            w,
            h
            ))
        self.render()


    def render(self) -> None:
        """ update the image """
        # TODO


class Meter(Text):
    """ class for a meter element in the game """

    # image: pygame.Surface
    # rect: pygame.Rect
    # text: str
    # color: pygame.Color
    textform: str | None
    progress: int
    threshhold: int
    use_bar: bool | None


    def __init__(
        self,
        text: str,
        xywh: Specs,
        threshold: int,
        use_bar: bool = False
        ) -> None:
        """ constructor """
        assert isinstance(threshold, int) \
            and threshold > 0, \
            "The argument `threshold` must be a positive \
            integer."
        self.threshhold = threshold
        assert isinstance(use_bar, bool), \
            "The argument `use_bar` must be a boolean."
        try:
            self.textform = text
            text = text.format(
                progress = 0, threshold = threshold
                )
            self.use_bar = use_bar
        except TypeError:
            self.textform = None
            self.use_bar = None
        super().__init__(text, xywh)


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
        self.progress = min(progress, self.threshhold)
        if self.textform is not None:
            self.retext(self.textform.format(
                progress = self.progress,
                threshold = self.threshhold
            ))
        self.render()


    def render(self) -> None:
        """ update the image """
        # TODO


Noner: TypeAlias = Callable[..., None]
def disable(function: Noner) -> Noner:
    """ disable functions if the game is over """
    @wraps(function)
    def wrapper(
        self: 'StrandGUI',
        *args: Any,
        **kwargs: Any
        ) -> None:
        """ disable wrapper """
        if self.game.game_over():
            return None
        return function(self, *args, **kwargs)
    return wrapper


class StrandGUI():
    """
    GUI for playing Strands
    """

    # Display
    canvas: pygame.Surface
    xb: int
    yb: int
    a: float
    clock: pygame.time.Clock

    # Game
    game: StrandsGameBase
    selected: StrandBase | None
    ## Visual Game Elements
    letters: pygame.sprite.Group[Letter]
    hint: Meter
    message: Text
    found: Meter
    theme: Text


    def __init__(self, game_file: str, mode: bool) -> None:
        """
        constructor

        Inputs:
            game_file (str): the string name of a file to
                load the game info from
            mode (bool): a boolean specifying whether to
                load the game as solved. If True, the game
                will show the solutions.
        """

        assert isinstance(mode, bool), \
            "The argument `mode` must be boolean."
        self.game = StrandsGame(game_file)

        pygame.init()
        pygame.display.set_caption(CAPTION)
        self.canvas = pygame.display.set_mode(
            self._size(True),
            pygame.RESIZABLE
            )
        self.clock = pygame.time.Clock()

        if mode:
            for _, strand in self.game.answers():
                self.selected = strand
                self._submit()


    def _size(self, init: bool = False) -> tuple[int, int]:
        """ scale the window for the board """
        rows = self.game.board().num_rows()
        cols = self.game.board().num_cols()
        w = round(rows * GRID_SIZE + 2 * BUFFER)
        h = round(
            cols * GRID_SIZE + 2 * BUFFER + HEADER + FOOTER
            )
        min_width, min_height = CANVAS_SIZE
        if w < min_width and h < min_height:
            self._resize(min_width, min_height, init)
            return CANVAS_SIZE
        else:
            self._resize(w, h, init)
            return (w, h)


    def _resize(
        self,
        w: int,
        h: int,
        init: bool = False
        ) -> None:
        """ scale the board for the window """

        rows = self.game.board().num_rows()
        cols = self.game.board().num_cols()
        board_width = rows * GRID_SIZE
        board_height = cols * GRID_SIZE + HEADER + FOOTER

        if rows > 0 and cols > 0:
            self.a = min(
                ((w - 2 * BUFFER) / board_width),
                ((h - 2 * BUFFER) / board_height)
                )
        else:
            self.a = 0

        self.xb = round((w - board_width * self.a) / 2)
        self.yb = round((h - board_height * self.a) / 2)

        if init:
            self._generate_elements()
        else:
            self._update_elements()


    def _generate_elements(self) -> None:
        """ generate all visual game elements """
        rows = self.game.board().num_rows()
        cols = self.game.board().num_cols()

        # generate letters
        self.letters = pygame.sprite.Group()
        for i in range(rows):
            for j in range(cols):
                pos = Pos(i, j)
                ch = self.game.board().get_letter(pos)
                x = round(self.a * i * GRID_SIZE + self.xb)
                y = round(
                    self.a * (HEADER + j * GRID_SIZE)
                    + self.yb
                    )
                w = round(self.a * GRID_SIZE)
                h = round(self.a * GRID_SIZE)
                self.letters.add(
                    Letter(pos, ch, (x, y, w, h))
                    )

        # generate footers
        max_w = round(
            1/2 * (self.canvas.get_width() - 2 * self.xb)
            )
        y = round(
            self.canvas.get_height() - self.yb
            - self.a * FOOTER
            )
        h = FOOTER
        self.hint = Meter(
            "HINT",
            (
                self.xb,
                y,
                round(min(3/2 * self.a * FOOTER, max_w)),
                h
                ),
            self.game.hint_threshold()
            )
        self.found = Meter(
            "Found {progress}/{threshold}",
            (
                max_w + self.xb,
                y,
                round(min(2 * self.a * FOOTER, max_w)),
                h
                ),
            len(self.game.answers())
            )

        # generate headers
        y = self.yb
        h = HEADER
        w = round(min(3 * self.a * HEADER, max_w))
        self.theme = Text(
            self.game.theme(),
            (
                self.xb,
                y,
                w,
                h
                ),
            )
        self.message = Text(
            "Good luck!",
            (
                self.xb + w,
                y,
                w,
                h
                ),
            )


    def _update_elements(self) -> None:
        """ update all visual game elements """

        # update letters
        self.letters.update(
            self.xb,
            round(self.yb + self.a * HEADER),
            round(self.a * GRID_SIZE),
            round(self.a * GRID_SIZE)
            )

        # update footers
        max_w = round(
            1/2 * (self.canvas.get_width() - 2 * self.xb)
            )
        y = round(
            self.canvas.get_height() - self.yb
            - self.a * FOOTER
            )
        h = FOOTER
        self.hint.resize((
            self.xb,
            y,
            round(min(3/2 * self.a * FOOTER, max_w)),
            h
            ))
        self.found.resize((
            max_w + self.xb,
            y,
            round(min(2 * self.a * FOOTER, max_w)),
            h
            ))

        # update headers
        y = self.yb
        h = HEADER
        w = round(min(3 * self.a * HEADER, max_w))
        self.theme.resize((
            self.xb,
            y,
            w,
            h
            ))
        self.message.resize((
            self.xb + w,
            y,
            w,
            h
            ))


    def play(self) -> None:
        """ Event Loop """

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._quit()

                elif event.type == pygame.KEYDOWN:
                    self._keydown(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    dragging = True
                    self._selecting(*event.pos)

                elif (
                    dragging and
                    event.type == pygame.MOUSEMOTION
                    ):
                    self._selecting(*event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging:
                        self._selected()
                    else:
                        self._click(*event.pos)
                    dragging = False

                elif event.type == pygame.VIDEORESIZE:
                    self._resize(*event.size)

            self._draw()
            self.clock.tick(FRAME_RATE)


    def _quit(self) -> None:
        """ quit the game """
        pygame.quit()
        sys.exit()


    @disable
    def _submit(self) -> None:
        """ submit a strand """
        if self.selected is None or not self.selected.steps:
            return
        info = self.game.submit_strand(self.selected)
        if isinstance(info, str):
            self.message.retext(info, TEXT_COLOR)
        else:
            word, theme = info
            if theme:
                self.message.retext(word, FOUND_COLOR)
                self.found.reprogress(
                    self.found.progress + 1
                    )
                self._update_found_letters()
                self._update_hint_letters()
            else:
                self.message.retext(word, SELECT_COLOR)
                self.hint.reprogress(self.game.hint_meter())
        self._deselect()

        if self.game.game_over():
            self.message.retext("You won!", TEXT_COLOR)


    @disable
    def _hint(self) -> None:
        """ use a hint if possible """
        info = self.game.use_hint()
        if isinstance(info, str):
            self.message.retext(info, TEXT_COLOR)
        else:
            self.hint.reprogress(self.game.hint_meter())
            self._update_hint_letters()


    def _deselect(self) -> None:
        """ deselect a strand """
        self.selected = None
        for letter in self.letters:
            letter.highlight_primary = None
            letter.render()


    @disable
    def _select(
        self,
        letter: Letter,
        dragging: bool
        ) -> None:
        """ select the letter given """
        # TODO


    def _keydown(self, key: int) -> None:
        """ process a keydown event """
        if key == pygame.K_q:
            self._quit()
        elif key == pygame.K_RETURN:
            self._submit()
        elif key == pygame.K_ESCAPE:
            self._deselect()
        elif key == pygame.K_h:
            self._hint()


    def _click(self, x: int, y: int) -> None:
        """ process a mouse click at the position given """
        if self.hint.rect.collidepoint(x, y):
            self._hint()
        # TODO: handle selecting vs sumbitting


    def _selecting(self, x: int, y: int) -> None:
        """ process mouse dragging at the position given """
        # TODO


    def _selected(self) -> None:
        """
        process the end of mouse dragging
        """
        # TODO


    def _draw(self) -> None:
        """ draw the display """
        # TODO


    def _update_hint_letters(self) -> None:
        """ update hint letters """
        # TODO


    def _update_found_letters(self) -> None:
        """ update found letters """
        # TODO


    def _connect(
        self,
        strand: StrandBase,
        color: pygame.Color
        ) -> None:
        """ connect a strand """
        # TODO
