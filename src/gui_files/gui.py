"""
Strands GUI Implementation
"""
# Amber

import sys
from typing import TypeAlias, Callable, Any
from functools import wraps
import pygame
from base import (
    StrandBase, StrandsGameBase
    )
from stubs import PosStub as Pos
from stubs import StrandsGameStub as StrandsGame
from gui_files.sprites import Text, Letter, Meter
from gui_files.settings import (
    HINT_THRESHOLD, CAPTION, FRAME_RATE, CANVAS_SIZE,
    GRID_SIZE, HEADER, FOOTER, BORDER,
    CANVAS_COLOR, TEXT_COLOR, SELECT_COLOR, FOUND_COLOR
    )

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
    adjustments: tuple[float, int, int]
    clock: pygame.time.Clock

    # Game
    game: StrandsGameBase
    selected: StrandBase | None
    ## Visual Game Elements
    letters: pygame.sprite.Group
    hint: Meter | Text
    message: Text
    found: Meter | Text
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
        self.game = StrandsGame(game_file, HINT_THRESHOLD)
        self.selected = None

        pygame.init()
        pygame.display.set_caption(CAPTION)
        self.canvas = pygame.display.set_mode(
            self._size(True),
            pygame.RESIZABLE
            )
        self._generate_elements()
        self.clock = pygame.time.Clock()

        if mode:
            for _, strand in self.game.answers():
                self.selected = strand
                self._submit()


    def _size(self, init: bool = False) -> tuple[int, int]:
        """ scale the window for the board """
        rows = self.game.board().num_rows()
        cols = self.game.board().num_cols()
        w = round(cols * GRID_SIZE + 2 * BORDER)
        h = round(
            rows * GRID_SIZE + 2 * BORDER + HEADER + FOOTER
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
        board_width = cols * GRID_SIZE
        board_height = rows * GRID_SIZE + HEADER + FOOTER

        if rows > 0 and cols > 0:
            a = min(
                ((w - 2 * BORDER) / board_width),
                ((h - 2 * BORDER) / board_height)
                )
        else:
            a = 0

        xb = round((w - board_width * a) / 2)
        yb = round((h - board_height * a) / 2)

        self.adjustments = (a, xb, yb)
        if not init:
            self._update_elements()


    def _generate_elements(self) -> None:
        """ generate all visual game elements """
        a, xb, yb = self.adjustments
        rows = self.game.board().num_rows()
        cols = self.game.board().num_cols()

        # generate letters
        self.letters = pygame.sprite.Group()
        for i in range(rows):
            for j in range(cols):
                pos = Pos(i, j)
                self.letters.add(Letter(
                    pos,
                    self.game.board().get_letter(pos),
                    (
                        round(a * j * GRID_SIZE + xb),
                        round(
                            a * (HEADER + i * GRID_SIZE)
                            + xb
                            ),
                        round(a * GRID_SIZE),
                        round(a * GRID_SIZE)
                        )
                    ))

        # generate texts
        canvas_w, canvas_h = self.canvas.get_size()
        max_w = round(1/2 * (canvas_w - 2 * xb))
        w = round(min(3 * a * HEADER, max_w))
        ## generate footers
        y = round(canvas_h - yb - a * FOOTER)
        h = round(FOOTER * a)
        if self.game.hint_threshold() == 0:
            self.hint = Text("HINT", (xb, y, w, h))
        else:
            self.hint = Meter(
                "HINT",
                (xb, y, w, h),
                self.game.hint_threshold(),
                True
                )
        self.hint.border = True
        self.hint.render()
        if len(self.game.answers()) == 0:
            self.found = Text("Found?", (xb + w, y, w, h))
        else:
            self.found = Meter(
                "Found {progress}/{threshold}",
                (xb + w, y, w, h),
                len(self.game.answers())
                )
        ## generate headers
        h = round(HEADER * a)
        self.theme = Text(
            self.game.theme(),
            (xb, yb, w, h)
            )
        self.message = Text(
            "Good luck!",
            (xb + w, yb, w, h)
            )


    def _update_elements(self) -> None:
        """ update all visual game elements """
        a, xb, yb = self.adjustments

        # update letters
        self.letters.update(
            xb,
            round(yb + a * HEADER),
            round(a * GRID_SIZE),
            round(a * GRID_SIZE)
            )

        # update texts
        canvas_w, canvas_h = self.canvas.get_size()
        max_w = round(1/2 * (canvas_w - 2 * xb))
        w = round(min(3 * a * HEADER, max_w))
        ## update footers
        y = round(canvas_h - yb - a * FOOTER)
        h = round(FOOTER * a)
        self.hint.resize((xb, y, w, h ))
        self.found.resize((xb + w, y, w, h))
        ## update headers
        y = yb
        h = round(HEADER * a)
        self.theme.resize((xb, y, w, h))
        self.message.resize((xb + w, y, w, h))


    def play(self) -> None:
        """ Event Loop """
        dragging = False
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
        # WARNING: commented out for milestone 1
        # if (
        #     self.selected is None
        #     or not self.selected.steps
        #     ):
        #     return

        # WARNING: Remove mypy override after milestone 1
        info = self.game.submit_strand(self.selected) # type: ignore
        if isinstance(info, str):
            self.message.retext(info, TEXT_COLOR)
        else:
            word, theme = info
            if theme:
                self._found_theme(word)
            else:
                self._found_other(word)
        self._deselect()

        if self.game.game_over():
            self.message.retext("You won!", TEXT_COLOR)


    def _found_theme(self, word: str) -> None:
        """ found a theme word """
        strand = self.game.found_strands()[-1]
        self.message.retext(word, FOUND_COLOR)
        if isinstance(self.found, Meter):
            self.found.reprogress(self.found.progress + 1)
        positions = strand.positions()
        for letter in self.letters:
            if letter.position in positions:
                letter.highlight_secondary = FOUND_COLOR
                letter.render()


    def _found_other(self, word: str) -> None:
        """ found a non-theme word """
        self.message.retext(word, SELECT_COLOR)
        if isinstance(self.hint, Meter):
            self.hint.reprogress(self.game.hint_meter())


    @disable
    def _hint(self) -> None:
        """ use a hint if possible """
        info = self.game.use_hint()
        if isinstance(info, str):
            self.message.retext(info, TEXT_COLOR)
        else:
            self._update_hint_letters()
            if not isinstance(self.hint, Meter):
                return
            self.hint.reprogress(self.game.hint_meter())


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
        # TODO: not required for milestone 1


    def _keydown(self, key: int) -> None:
        """ process a keydown event with the given key """
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
        # TODO: not required for milestone 1
        #       handle selecting vs submitting logic


    def _selecting(self, x: int, y: int) -> None:
        """
        process mouse dragging at the position given
        """
        # TODO: not required for milestone 1


    def _selected(self) -> None:
        """
        process the end of mouse dragging
        """
        # TODO: not required for milestone 1


    def _draw(self) -> None:
        """ draw the display """
        self.canvas.fill(CANVAS_COLOR)
        self._draw_borders()
        for strand in self.game.found_strands():
            self._connect(strand, FOUND_COLOR)
        if self.selected is not None:
            self._connect(self.selected, SELECT_COLOR)
        self.letters.draw(self.canvas)
        pygame.sprite.Group(
            self.theme, self.message, self.hint, self.found
            ).draw(self.canvas)
        pygame.display.update()


    def _draw_borders(self) -> None:
        """ draw borders """
        _, xb, yb = self.adjustments
        w, h = self.canvas.get_size()
        pygame.draw.rect(
            self.canvas,
            SELECT_COLOR,
            pygame.Rect(0, 0, w, yb)
            )
        pygame.draw.rect(
            self.canvas,
            SELECT_COLOR,
            pygame.Rect(0, 0, xb, h)
            )
        pygame.draw.rect(
            self.canvas,
            SELECT_COLOR,
            pygame.Rect(0, h - yb, w, yb)
            )
        pygame.draw.rect(
            self.canvas,
            SELECT_COLOR,
            pygame.Rect(w - xb, 0, xb, h)
            )


    def _update_hint_letters(self) -> None:
        """ update hint letters """
        # TODO: not required for milestone 1


    def _connect(
        self,
        strand: StrandBase,
        color: pygame.Color
        ) -> None:
        """ connect a strand """
        # TODO: not required for milestone 1
