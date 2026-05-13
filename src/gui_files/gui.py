"""
Strands GUI Implementation
"""
# Amber

import sys
from typing import NamedTuple
import pygame
from base import (
    StrandBase, StrandsGameBase, PosBase
    )
from strands import Pos, Strand, StrandsGame
from gui_files.sprites import Text, Letter, Meter, Specs
from gui_files.settings import (
    HINT_THRESHOLD, CAPTION, FRAME_RATE,
    GRID_SIZE, ELEMENT_BUFFER,
    CANVAS_SIZE, HEADER, FOOTER, BORDER,
    SELECT_COLOR, CANVAS_COLOR, TEXT_COLOR, BORDER_COLOR,
    HINT_COLOR, FOUND_COLOR, UNTHEME_COLOR,
    )


class Adjustments(NamedTuple):
    """ (a, xb, yb) """
    a: float # scaling factor
    xb: int # x border size
    yb: int # y border size


class InfoSpecs(NamedTuple):
    """ (theme, message, hint, found) """
    theme: Specs
    message: Specs
    hint: Specs
    found: Specs


class StrandGUI():
    """
    GUI for playing Strands
    """

    # the main display window
    _canvas: pygame.Surface

    # (scaling factor, x border, y border)
    # for sizing and positioning adjustments of the board
    _adj: Adjustments

    # used to maintain frame rate
    _clock: pygame.time.Clock

    # contains the game logic and the current state
    _game: StrandsGameBase

    # the currently selected strand, if any
    _select: StrandBase | None

    # a sprite group for all the letters on the board
    _letters: pygame.sprite.Group

    # used for looking up letters by their position
    _letters_lookup: dict[tuple[int, int], Letter]

    # the hint button sprite
    _hint: Meter | Text

    # a sprite for displaying game messages
    _message: Text

    # a sprite for displaying the game progress
    # the number of theme words found and the total to find
    _found: Meter | Text

    # a sprite for displaying the game theme
    _theme: Text


    def __init__(self, game_file: str, mode: bool) -> None:
        """
        Load a game!

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
        if not isinstance(game_file, str):
            raise TypeError(
                "The argument `game_file` must be a "
                "string."
                )
        self._game = StrandsGame(game_file, HINT_THRESHOLD)
        pygame.init()
        pygame.display.set_caption(CAPTION)
        self._canvas = pygame.display.set_mode(
            self._size(),
            pygame.RESIZABLE
            )
        self._clock = pygame.time.Clock()
        self._select = None
        self._generate_sprites()
        if mode:
            for _, strand in self._game.answers():
                self._select = strand
                self._submitter()


    def _size(self) -> tuple[int, int]:
        """
        scale the canvas for the board

        If the canvas width and canvas height to fit the
        board are calculated to be below the minimum width
        and minimum height, the canvas width and height
        are set to the minimum width and height and the
        board is rescaled.

        If the scaling factor is calculated to be negative,
        it is set to 0.

        The calculated scaling factor, x border, and y
        border are saved in the `_adjustments` attribute,
        in that order.

        Raises AssertionError if the board width or board
        height are calculated to be nonpositive somehow.

        Returns the canvas width and height as a tuple.
        """
        rows = self._game.board().num_rows()
        cols = self._game.board().num_cols()
        board_width = cols * GRID_SIZE
        board_height = rows * GRID_SIZE + HEADER + FOOTER
        assert board_width > 0 and board_height > 0, \
            "The display board must have positive height \
            and width."
        canvas_width = board_width + 2 * BORDER
        canvas_height = board_height + 2 * BORDER
        min_width, min_height = CANVAS_SIZE
        if (
            canvas_width > min_width
            or canvas_height > min_height
            ):
            self._adj = Adjustments(1, BORDER, BORDER)
            return (canvas_width, canvas_height)
        a = min(
            ((min_width - 2 * BORDER) / board_width),
            ((min_height - 2 * BORDER) / board_height)
            )
        a = max(a, 0)
        self._adj = Adjustments(
            a,
            round((min_width - board_width * a) / 2),
            round((min_height - board_height * a) / 2)
            )
        return (min_width, min_height)


    def _resize(self, w: int, h: int) -> None:
        """
        process a video resize event with the given size

        If the scaling factor is calculated to be negative,
        it is set to 0.

        The calculated scaling factor, x border, and y
        border are saved in the `_adjustments` attribute,
        in that order.

        The sprites are updated and the display is
        re-rendered.

        Inputs:
            w (int): the canvas width
            h (int): the canvas height

        Raises AssertionError if the board width or board
        height are calculated to be nonpositive somehow.
        """
        rows = self._game.board().num_rows()
        cols = self._game.board().num_cols()
        board_width = cols * GRID_SIZE
        board_height = rows * GRID_SIZE + HEADER + FOOTER
        assert board_width > 0 and board_height > 0, (
            "The display board must have positive height "
            "and width."
            )
        a = min(
            ((w - 2 * BORDER) / board_width),
            ((h - 2 * BORDER) / board_height)
            )
        a = max(a, 0)
        xb = round((w - board_width * a) / 2)
        yb = round((h - board_height * a) / 2)
        self._adj = Adjustments(a, xb, yb)
        self._update_sprites()
        self._render()


    def _generate_sprites(self) -> None:
        """ generate all sprites """

        # generate letters
        a, xb, yb = self._adj
        self._letters_lookup = {}
        self._letters = pygame.sprite.Group()
        grid = a * GRID_SIZE
        for i in range(self._game.board().num_rows()):
            for j in range(self._game.board().num_cols()):
                pos = Pos(i, j)
                letter = Letter(
                    pos,
                    self._game.board().get_letter(pos),
                    Specs(
                        round((j + 1/2) * grid + xb),
                        round(
                            (i + 1/2) * grid
                            + yb + a * HEADER
                            ),
                        round(ELEMENT_BUFFER * grid),
                        round(ELEMENT_BUFFER * grid)
                        )
                    )
                letter.render()
                self._letters.add(letter)
                self._letters_lookup[(i, j)] = letter

        # generate info sprites
        specs = self._spec_info()
        self._theme = Text(self._game.theme(), specs.theme)
        self._theme.render()
        self._message = Text("Good luck!", specs.message)
        self._message.render()
        if self._game.hint_threshold() <= 0:
            self._hint = Text("HINT", specs.hint, True)
        else:
            self._hint = Meter(
                "HINT",
                specs.hint,
                self._game.hint_threshold(),
                True
                )
        self._hint.render()
        if len(self._game.answers()) == 0:
            self._found = Text("Found?", specs.found)
        else:
            self._found = Meter(
                "Found {meter}/{threshold}",
                specs.found,
                len(self._game.answers())
                )
        self._found.render()


    def _spec_info(self) -> InfoSpecs:
        """
        calculate the sizes and positions for the info
        sprites

        Returns (InfoSpecs):
        - The sizes and positions for the info sprites
        """
        a, xb, yb = self._adj
        canvas_w, canvas_h = self._canvas.get_size()

        # shared values
        max_w = max(1/2 * (canvas_w - 2 * xb), 0)
        left_x = round(xb + 1/2 * max_w)
        right_x = round(xb + 3/2 * max_w)
        # header-specific
        header_h = a * HEADER
        header_y = round(yb + 1/2 * header_h)
        header_w = round(
            ELEMENT_BUFFER * min(3 * header_h, max_w)
            )
        header_h = round(ELEMENT_BUFFER * header_h)
        # footer-specific
        footer_h = a * FOOTER
        footer_y = round(canvas_h - yb - 1/2 * footer_h)
        footer_w = round(
            ELEMENT_BUFFER * min(3 * footer_h, max_w)
            )
        footer_h = round(ELEMENT_BUFFER * footer_h)

        return InfoSpecs(
            Specs(left_x, header_y, header_w, header_h),
            Specs(right_x, header_y, header_w, header_h),
            Specs(left_x, footer_y, footer_w, footer_h),
            Specs(right_x, footer_y, footer_w, footer_h)
            )


    def _update_sprites(self) -> None:
        """ update all sprites after a resizing """
        # update letters
        a, xb, yb = self._adj
        self._letters.update(
            (xb, round(yb + a * HEADER)),
            round(a * GRID_SIZE),
            round(ELEMENT_BUFFER * a * GRID_SIZE)
            )
        # update info sprites
        specs = self._spec_info()
        self._hint.resize(specs.hint)
        self._hint.render()
        self._found.resize(specs.found)
        self._found.render()
        self._theme.resize(specs.theme)
        self._theme.render()
        self._message.resize(specs.message)
        self._message.render()


    def play(self) -> None:
        """ Play the game! """
        self._render()
        # flags to allow for click-dragging the mouse
        held = False
        dragging = False
        interrupt = False
        # Event Loop
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._quit()
                elif event.type == pygame.KEYDOWN:
                    self._keydown(event.key)
                    interrupt = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    held = True
                    interrupt = False
                elif (
                    held
                    and event.type == pygame.MOUSEMOTION
                    and any(abs(n) > 2 for n in event.rel)
                    ):
                    # the minimum event.rel was added to
                    # prevent unintentional click-dragging
                    dragging = True
                    interrupt = False
                    self._selecting(*event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if interrupt:
                        pass
                    elif dragging:
                        self._selected()
                    else:
                        self._click(*event.pos)
                    dragging = False
                    held = False
                    interrupt = False
                elif event.type == pygame.VIDEORESIZE:
                    self._resize(*event.size)
            self._clock.tick(FRAME_RATE)


    def _quit(self) -> None:
        """ process a quit event """
        pygame.quit()
        sys.exit()


    def _submitter(self) -> None:
        """ submit a strand """
        if self._game.game_over():
            return
        if self._select is None:
            self._message.retext(
                "Nothing selected",
                TEXT_COLOR
                )
            self._message.render()
            return
        info = self._game.submit_strand(self._select)
        if isinstance(info, str):
            self._message.retext(info, TEXT_COLOR)
            self._message.render()
        else:
            word, is_theme = info
            if is_theme:
                if self._game.game_over():
                    self._message.retext(
                        "You won!",
                        TEXT_COLOR
                        )
                else:
                    self._message.retext(word, FOUND_COLOR)
                self._message.render()
                if isinstance(self._found, Meter):
                    self._found.remeter(
                        len(self._game.found_strands())
                        )
                    self._found.render()
                strand = self._game.found_strands()[-1]
                for pos in strand.positions():
                    position = (pos.r, pos.c)
                    letter = self._letters_lookup[position]
                    letter.highlight2 = FOUND_COLOR
                    letter.border = False
                    letter.render()
            else:
                self._message.retext(word, UNTHEME_COLOR)
                self._message.render()
                if isinstance(self._hint, Meter):
                    self._hint.remeter(
                        self._game.hint_meter()
                        )
                    self._hint.render()
        self._deselecter()


    def _hinter(self) -> None:
        """ use a hint """
        if self._game.game_over():
            return
        info = self._game.use_hint()
        if isinstance(info, str):
            self._message.retext(info, TEXT_COLOR)
            self._message.render()
        else:
            i, b = info
            _, strand = self._game.answers()[i]
            positions = strand.positions()
            first_last = (positions[0], positions[-1])
            for pos in positions:
                position = (pos.r, pos.c)
                letter = self._letters_lookup[position]
                letter.highlight2 = HINT_COLOR
                if b and pos in first_last:
                    letter.border = True
                letter.render()
            if isinstance(self._hint, Meter):
                self._hint.remeter(self._game.hint_meter())
                self._hint.render()


    def _deselecter(self) -> None:
        """ deselect a strand """
        if self._select is None:
            return
        for pos_ in self._select.positions():
            position = (pos_.r, pos_.c)
            letter = self._letters_lookup[position]
            letter.highlight1 = None
            letter.render()
        self._select = None


    def _selecter(
        self,
        pos: PosBase,
        dragging: bool
        ) -> None:
        """
        interact with the letter at the given position,
        with the flag `dragging` to allow for continuous
        selection when click-dragging
        """
        if self._game.game_over():
            return

        # update selection
        if self._select is None:
            new = Strand(pos, [])
        else:
            *positions, last = self._select.positions()
            if pos == last:
                # allow continuous selection if
                # click-dragging
                if dragging:
                    return
                # deselect if clicking the only letter
                # selected
                elif not positions:
                    new = None
                # submit if clicking the last letter
                # selected
                else:
                    self._submitter()
                    return
            # backtrack the selection to the given pos
            elif pos in positions:
                i = positions.index(pos)
                new = Strand(
                    self._select.start,
                    self._select.steps[:i]
                    )
            # extend the selection to the given pos
            elif pos.is_adjacent_to(last):
                new = Strand(
                    self._select.start,
                    self._select.steps + [last.step_to(pos)]
                    )
            else:
                new = None

        # update letter sprites
        self._deselecter() # clear the previous render first
        if new is not None:
            for pos_ in new.positions():
                position = (pos_.r, pos_.c)
                letter = self._letters_lookup[position]
                letter.highlight1 = SELECT_COLOR
                letter.render()
        self._select = new


    def _founder(self) -> None:
        """ show the number of words left in a message """
        if self._game.game_over():
            return
        left = (
            len(self._game.answers())
            - len(self._game.found_strands())
            )
        self._message.retext(
            f"Only {left} left!",
            TEXT_COLOR
            )
        self._message.render()


    def _keydown(self, key: int) -> None:
        """ process a keydown event with the given key """
        if key == pygame.K_q:
            self._quit()
        elif key == pygame.K_RETURN:
            self._submitter()
        elif key == pygame.K_ESCAPE:
            self._deselecter()
        elif key == pygame.K_h:
            self._hinter()
        self._render()


    def _click(self, x: int, y: int) -> None:
        """ process a mouse click at the position given """
        if self._hint.rect.collidepoint(x, y):
            self._hinter()
        elif self._found.rect.collidepoint(x, y):
            self._founder()
        else:
            for letter in self._letters:
                if letter.rect.collidepoint(x, y):
                    self._selecter(letter.position, False)
                    break
        self._render()


    def _selecting(self, x: int, y: int) -> None:
        """ process mouse dragging at the position given """
        for letter in self._letters:
            if letter.rect.collidepoint(x, y):
                self._selecter(letter.position, True)
                break
        self._render()


    def _selected(self) -> None:
        """ process the end of mouse dragging """
        self._submitter()
        self._render()


    def _render(self) -> None:
        """ render the display """
        self._canvas.fill(CANVAS_COLOR)
        self._draw_borders()
        for strand in self._game.found_strands():
            self._connect(strand, FOUND_COLOR)
        if self._select is not None:
            self._connect(self._select, SELECT_COLOR)
        self._letters.draw(self._canvas)
        pygame.sprite.Group(
            self._theme, self._message,
            self._hint, self._found
            ).draw(self._canvas)
        pygame.display.update()


    def _draw_borders(self) -> None:
        """ draw borders """
        _, xb, yb = self._adj
        w, h = self._canvas.get_size()
        pygame.draw.rect(
            self._canvas,
            BORDER_COLOR,
            pygame.Rect(0, 0, w, yb)
            )
        pygame.draw.rect(
            self._canvas,
            BORDER_COLOR,
            pygame.Rect(0, 0, xb, h)
            )
        pygame.draw.rect(
            self._canvas,
            BORDER_COLOR,
            pygame.Rect(0, h - yb, w, yb)
            )
        pygame.draw.rect(
            self._canvas,
            BORDER_COLOR,
            pygame.Rect(w - xb, 0, xb, h)
            )


    def _connect(
        self,
        strand: StrandBase,
        color: pygame.Color
        ) -> None:
        """
        draw the connections between letters of a strand

        Inputs:
            strand (Strand): the strand to draw
                connections for
            color (pygame.Color): the color to draw the
                connections with
        """
        radius = round(self._adj.a/3 * GRID_SIZE)
        def __connect(
            positions: list[PosBase]
            ) -> tuple[int, int]:
            """
            recursively draw lines between the centers of
            the letters at each position given

            Input:
                positions (list[PosBase]): a list of
                    positions on the board to draw lines
                    between
            Output (tuple[int, int]):
                - The x, y center coordinates of the
                    letter sprite corresponding to the
                    last position in the list.
            """
            if len(positions) == 1:
                position = (positions[0].r, positions[0].c)
                letter = self._letters_lookup[position]
                return letter.rect.center
            start = __connect(positions[:-1])
            stop = __connect(positions[-1:])
            pygame.draw.line(
                self._canvas,
                color,
                start,
                stop,
                radius
                )
            return stop
        __connect(strand.positions())
