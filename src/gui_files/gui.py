"""
Strands GUI Implementation
"""
# Amber

import sys
import pygame
from base import (
    StrandBase, StrandsGameBase, PosBase
    )
from stubs import StrandsGameStub as StrandsGame
from finals.strand import Strand
from finals.pos import Pos
from gui_files.sprites import Text, Letter, Meter
from gui_files.settings import (
    HINT_THRESHOLD, CAPTION, FRAME_RATE,
    CANVAS_SIZE, GRID_SIZE, HEADER, FOOTER, BORDER,
    CANVAS_COLOR, TEXT_COLOR, SELECT_COLOR,
    HINT_COLOR, FOUND_COLOR
    )


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
    select: StrandBase | None
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
        if not isinstance(mode, bool):
            raise TypeError(
                "The argument `mode` must be boolean."
                )

        self.game = StrandsGame(game_file, HINT_THRESHOLD)
        self.select = None

        pygame.init()
        pygame.display.set_caption(CAPTION)
        self.canvas = pygame.display.set_mode(
            self._size(),
            pygame.RESIZABLE
            )
        self.clock = pygame.time.Clock()

        self._generate_elements()
        if mode:
            for _, strand in self.game.answers():
                self.select = strand
                self._submit()


    def _size(self) -> tuple[int, int]:
        """ scale the canvas for the board """
        rows = self.game.board().num_rows()
        cols = self.game.board().num_cols()
        board_width = cols * GRID_SIZE
        board_height = rows * GRID_SIZE + HEADER + FOOTER
        canvas_width = board_width + 2 * BORDER
        canvas_height = board_height + 2 * BORDER
        min_width, min_height = CANVAS_SIZE
        if (
            canvas_width > min_width
            or canvas_height > min_height
            ):
            self.adjustments = (1, BORDER, BORDER)
            return (canvas_width, canvas_height)
        if rows > 0 and cols > 0:
            a = min(
                ((min_width - 2 * BORDER) / board_width),
                ((min_height - 2 * BORDER) / board_height)
                )
        else:
            a = 0
        self.adjustments = (
            a,
            round((min_width - board_width * a) / 2),
            round((min_height - board_height * a) / 2)
            )
        return (min_width, min_height)


    def _resize(self, w: int, h: int) -> None:
        """ scale the board for the canvas """
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
        self._update_elements()
        self._render()


    def _generate_elements(self) -> None:
        """ generate all visual game elements """
        a, xb, yb = self.adjustments

        # generate letters
        self.letters = pygame.sprite.Group()
        for i in range(self.game.board().num_rows()):
            for j in range(self.game.board().num_cols()):
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
            self.hint = Text("HINT", (xb, y, w, h), True)
        else:
            self.hint = Meter(
                "HINT",
                (xb, y, w, h),
                self.game.hint_threshold(),
                True
                )
        self.hint.render()
        if len(self.game.answers()) == 0:
            self.found = Text("Found?", (xb + w, y, w, h))
        else:
            self.found = Meter(
                "Found {meter}/{threshold}",
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
        """
        update all visual game elements after a resizing
        """

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
        self._render()
        held = False
        dragging = False
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._quit()
                elif event.type == pygame.KEYDOWN:
                    self._keydown(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    held = True
                elif (
                    held
                    and event.type == pygame.MOUSEMOTION
                    and any(abs(n) > 2 for n in event.rel)
                    ):
                    dragging = True
                    self._selecting(*event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging:
                        self._selected()
                    else:
                        self._click(*event.pos)
                    dragging = False
                    held = False
                elif event.type == pygame.VIDEORESIZE:
                    self._resize(*event.size)
            self.clock.tick(FRAME_RATE)


    def _quit(self) -> None:
        """ quit the game """
        pygame.quit()
        sys.exit()


    def _submit(self) -> None:
        """ submit a strand """
        # WARNING: commented out for milestone 1
        # if (
        #     self.game.game_over()
        #     or self.select is None
        #     or not self.select.steps
        #     ):
        #     return

        # WARNING: Remove mypy override after milestone 1
        info = self.game.submit_strand(self.select) # type: ignore
        if isinstance(info, str):
            self.message.retext(info, TEXT_COLOR)
        else:
            word, theme = info
            if theme:
                strand = self.game.found_strands()[-1]
                self.message.retext(word, FOUND_COLOR)
                if isinstance(self.found, Meter):
                    self.found.remeter(
                        len(self.game.found_strands())
                        )
                positions = strand.positions()
                for letter in self.letters:
                    if letter.position in positions:
                        letter.highlight2 = FOUND_COLOR
                        letter.border = False
                        letter.render()
            else:
                self.message.retext(word, SELECT_COLOR)
                if isinstance(self.hint, Meter):
                    self.hint.remeter(
                        self.game.hint_meter()
                        )
        self._deselect()
        if self.game.game_over():
            self.message.retext("You won!", TEXT_COLOR)


    def _hint(self) -> None:
        """ use a hint """
        if self.game.game_over():
            return
        info = self.game.use_hint()
        if isinstance(info, str):
            self.message.retext(info, TEXT_COLOR)
        else:
            i, b = info
            # WARNING: Change int(i) to i after milestone 1
            _, strand = self.game.answers()[int(i)]
            positions = strand.positions()
            first_last = (positions[0], positions[-1])
            for letter in self.letters:
                if letter.position in positions:
                    letter.highlight2 = HINT_COLOR
                    if b and letter.position in first_last:
                        letter.border = True
                    letter.render()
            if isinstance(self.hint, Meter):
                self.hint.remeter(self.game.hint_meter())


    def _deselect(self) -> None:
        """ deselect a strand """
        if self.game.game_over() or self.select is None:
            return
        positions = self.select.positions()
        for letter in self.letters:
            if letter.position in positions:
                letter.highlight1 = None
                letter.render()
        self.select = None


    def _select(
        self,
        pos: PosBase,
        dragging: bool
        ) -> None:
        """
        interact with the letter at the given position
        """
        if self.game.game_over():
            return

        # save old selection and wipe
        old = self.select
        self._deselect()

        # update selection
        new: StrandBase | None = None
        if old is None:
            new = Strand(pos, [])
        else:
            *positions, last = old.positions()
            if pos == last:
                if dragging:
                    new = old
                else:
                    self._submit()
            elif pos in positions:
                i = positions.index(pos)
                new = Strand(old.start, old.steps[:i])
            elif pos.is_adjacent_to(last):
                new = Strand(
                    old.start,
                    old.steps + [last.step_to(pos)]
                    )
            else:
                self._submit()
        self.select = new

        # update letter sprites
        if new is not None:
            positions = new.positions()
            for letter in self.letters:
                if letter.position in positions:
                    letter.highlight1 = SELECT_COLOR
                    letter.render()


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
        self._render()


    def _click(self, x: int, y: int) -> None:
        """ process a mouse click at the position given """
        if self.hint.rect.collidepoint(x, y):
            self._hint()
        for letter in self.letters:
            if letter.rect.collidepoint(x, y):
                self._select(letter.position, False)
                break
        self._render()


    def _selecting(self, x: int, y: int) -> None:
        """
        process mouse dragging at the position given
        """
        for letter in self.letters:
            if letter.rect.collidepoint(x, y):
                self._select(letter.position, True)
                break
        self._render()


    def _selected(self) -> None:
        """
        process the end of mouse dragging
        """
        self._submit()
        self._render()


    def _render(self) -> None:
        """ render the display """
        self.canvas.fill(CANVAS_COLOR)
        self._draw_borders()
        for strand in self.game.found_strands():
            self._connect(strand.positions(), FOUND_COLOR)
        if self.select is not None:
            self._connect(
                self.select.positions(),
                SELECT_COLOR
                )
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


    def _connect(
        self,
        positions: list[PosBase],
        color: pygame.Color
        ) -> tuple[int, int]:
        """ connect a list of positions on the board """
        if len(positions) == 1:
            for letter in self.letters:
                if letter.position == positions[0]:
                    return letter.rect.center
        start = self._connect(positions[:-1], color)
        stop = self._connect(positions[-1:], color)
        pygame.draw.line(
            self.canvas,
            color,
            start,
            stop,
            round(1/3 * self.adjustments[0] * GRID_SIZE)
            )
        return stop
