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


class App:
    """ constants for StrandsGUI """

    # the caption for the pygame window
    CAPTION: str = "Strands"

    # the refresh rate for the pygame window
    FRAME_RATE: int = 24

    # the minimum relative movement required to trigger
    # click-dragging
    MIN_REL: int = 2

    # the minimum pygame window size when launching
    CANVAS_SIZE: tuple[int, int] = (600, 600)

    # the standard x and y spacing of letters on the board
    GRID_SIZE: tuple[int, int] = (60, 60)

    # the standard height for the header of the board
    HEADER: int = 50

    # the standard height for the footer of the board
    FOOTER: int = 50

    # the standard size for the x and y border around the
    # board
    BORDER: tuple[int, int] = (25, 25)

    # used by StrandsGUI to scale sprites to add space
    # between and around sprites in the pygame window
    ELEMENT_BUFFER: float = 1 - 1/4

    # the default aspect ratio for info sprites
    INFO_AR: float = 3

    # the starting text for the message sprite
    MESSAGE_START: str = "Good luck!"

    # the winning text for the message sprite
    MESSAGE_WIN: str = "You win!"

    # the text if submitting nothing for the message sprite
    MESSAGE_EMPTY_SUBMIT: str = "Nothing selected"

    # the text if clicking on the found sprite
    MESSAGE_FOUND: str = "Only {left} left!"

    # the text for the hint sprite if it is a Text object
    HINT_TEXT: str = "HINT"

    # the text for the hint sprite if it is a Meter object
    HINT_METER: str = "HINT"

    # the text for the found sprite if it is a Text object
    FOUND_TEXT: str = "Found?"

    # the text for the found sprite if it is a Meter object
    FOUND_METER: str = "Found {meter}/{threshold}"

    # the scaling factor for the strand connection lines
    CONNECT_SCALE: float = 1/3

    # the background color of the canvas
    CANVAS_COLOR: pygame.Color = pygame.Color("white")

    # the default color of text
    TEXT_COLOR: pygame.Color = pygame.Color("black")

    # the color used to show selected strands
    SELECT_COLOR: pygame.Color = pygame.Color("lightgray")

    # the color used to show dictionary words when found
    UNTHEME_COLOR: pygame.Color = pygame.Color("black")

    # the color used to show active hints
    HINT_COLOR: pygame.Color = pygame.Color("lavender")

    # the color used to show found words
    FOUND_COLOR: pygame.Color = pygame.Color("lightskyblue")

    # the color of the border around the board
    BORDER_COLOR: pygame.Color = pygame.Color("snow2")


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


    def __init__(
        self,
        game: str,
        mode: bool,
        hint_threshold: int | None = None
        ) -> None:
        """
        Load a game!

        Inputs:
            game_file (str): the string name of a file to
                load the game info from
            mode (bool): a boolean specifying whether to
                load the game as solved. If True, the game
                will show the solutions.
            hint_threshold (int | None): The hint threshold
                as a nonnegative integer or None to use the
                default.
        """
        if not isinstance(mode, bool):
            raise TypeError(
                "The argument `mode` must be boolean."
                )
        if not isinstance(game, str):
            raise TypeError(
                "The argument `game` must be a string."
                )
        if hint_threshold is not None:
            if not isinstance(hint_threshold, int):
                raise TypeError(
                    "The argument `hint_threshold` must "
                    "be a nonnegative integer."
                    )
            if hint_threshold < 0:
                raise ValueError(
                    "The argument `hint_threshold` must "
                    "be a nonnegative integer."
                    )
            self._game = StrandsGame(game, hint_threshold)
        else:
            self._game = StrandsGame(game)
        pygame.init()
        pygame.display.set_caption(App.CAPTION)
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


    # SIZING METHODS

    def _size(
        self,
        size: tuple[int, int] | None = None
        ) -> tuple[int, int]:
        """
        scale the canvas and/or board

        Inputs:
            size (tuple[int, int] | None): the size of the
                canvas or None to size the canvas using the
                board

        If the argument `size` is None and the canvas width
        and canvas height to fit the board are calculated
        to be below the minimum width and minimum height,
        the canvas width and height are set to the minimum
        width and height and the board is rescaled.

        If the argument `size` is given, the board is
        rescaled to fit the given size. If the scaling
        factor is calculated to be negative, it is set to
        0.

        The calculated scaling factor, x border, and y
        border are saved in the `_adjustments` attribute,
        in that order.

        Raises AssertionError if the board width or board
        height are calculated to be nonpositive somehow.

        Returns the canvas width and height as a tuple.
        """
        rows = self._game.board().num_rows()
        cols = self._game.board().num_cols()
        grid_x, grid_y = App.GRID_SIZE
        border_x, border_y = App.BORDER
        board_width = cols * grid_x
        board_height = (
            rows * grid_y + App.HEADER + App.FOOTER
            )
        assert board_width > 0 and board_height > 0, (
            "The display board must have positive height "
            "and width."
            )
        if size is None:
            canvas_width = board_width + 2 * border_x
            canvas_height = board_height + 2 * border_y
            min_width, min_height = App.CANVAS_SIZE
            if (
                canvas_width > min_width
                or canvas_height > min_height
                ):
                self._adj = Adjustments(
                    1, border_x, border_y
                    )
                return (canvas_width, canvas_height)
            canvas_width, canvas_height = App.CANVAS_SIZE
        else:
            canvas_width, canvas_height = size
        a = min(
            ((canvas_width - 2 * border_x) / board_width),
            ((canvas_height - 2 * border_y) / board_height)
            )
        a = max(a, 0)
        self._adj = Adjustments(
            a,
            round((canvas_width - board_width * a) / 2),
            round((canvas_height - board_height * a) / 2)
            )
        return (canvas_width, canvas_height)


    def _generate_sprites(self) -> None:
        """ generate all sprites """

        # generate letters
        a, xb, yb = self._adj
        self._letters_lookup = {}
        self._letters = pygame.sprite.Group()
        grid_x, grid_y = (a * n for n in App.GRID_SIZE)
        for i in range(self._game.board().num_rows()):
            for j in range(self._game.board().num_cols()):
                pos = Pos(i, j)
                letter = Letter(
                    pos,
                    self._game.board().get_letter(pos),
                    Specs(
                        round((j + 1/2) * grid_x + xb),
                        round(
                            (i + 1/2) * grid_y
                            + yb + a * App.HEADER
                            ),
                        round(App.ELEMENT_BUFFER * grid_x),
                        round(App.ELEMENT_BUFFER * grid_y)
                        )
                    )
                letter.render()
                self._letters.add(letter)
                self._letters_lookup[(i, j)] = letter

        # generate then render all info sprites
        specs = self._spec_info()
        self._theme = Text(self._game.theme(), specs.theme)
        self._message = Text(
            App.MESSAGE_START,
            specs.message
            )
        if self._game.hint_threshold() <= 0:
            self._hint = Text(App.HINT_TEXT, specs.hint)
            self._hint.border = True
        else:
            self._hint = Meter(
                App.HINT_METER,
                specs.hint,
                self._game.hint_threshold(),
                True
                )
        if len(self._game.answers()) == 0:
            self._found = Text(App.FOUND_TEXT, specs.found)
        else:
            self._found = Meter(
                App.FOUND_METER,
                specs.found,
                len(self._game.answers())
                )
        self._theme.render()
        self._message.render()
        self._hint.render()
        self._found.render()


    def _update_sprites(self) -> None:
        """ update all sprites after a resizing """
        # update letters
        a, xb, yb = self._adj
        grid_x, grid_y = (a * n for n in App.GRID_SIZE)
        self._letters.update(
            (xb, round(yb + a * App.HEADER)),
            (round(grid_x), round(grid_y)),
            (
                round(App.ELEMENT_BUFFER * grid_x),
                round(App.ELEMENT_BUFFER * grid_y)
                )
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
        header_h = a * App.HEADER
        header_y = round(yb + 1/2 * header_h)
        header_w = round(
            App.ELEMENT_BUFFER
            * min(App.INFO_AR * header_h, max_w)
            )
        header_h = round(App.ELEMENT_BUFFER * header_h)
        # footer-specific
        footer_h = a * App.FOOTER
        footer_y = round(canvas_h - yb - 1/2 * footer_h)
        footer_w = round(
            App.ELEMENT_BUFFER
            * min(App.INFO_AR * footer_h, max_w)
            )
        footer_h = round(App.ELEMENT_BUFFER * footer_h)

        return InfoSpecs(
            Specs(left_x, header_y, header_w, header_h),
            Specs(right_x, header_y, header_w, header_h),
            Specs(left_x, footer_y, footer_w, footer_h),
            Specs(right_x, footer_y, footer_w, footer_h)
            )


    # USER INPUT METHODS

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
                    and any(
                            abs(n) > App.MIN_REL
                            for n in event.rel
                            )
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
                    self._resize(event.size)
            self._clock.tick(App.FRAME_RATE)


    def _quit(self) -> None:
        """ process a quit event """
        pygame.quit()
        sys.exit()


    def _resize(self, size: tuple[int, int]) -> None:
        """
        process a video resize event with the given size
        """
        self._size(size)
        self._update_sprites()
        self._render()


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


    # GAME PLAY METHODS

    def _submitter(self) -> None:
        """ submit a strand """
        if self._game.game_over():
            return
        if self._select is None:
            self._message.text = App.MESSAGE_EMPTY_SUBMIT
            self._message.text_color = App.TEXT_COLOR
            self._message.render()
            return
        info = self._game.submit_strand(self._select)
        if isinstance(info, str):
            self._message.text = info
            self._message.text_color = App.TEXT_COLOR
            self._message.render()
        else:
            word, is_theme = info
            if is_theme:
                if self._game.game_over():
                    self._message.text = App.MESSAGE_WIN
                    self._message.text_color = (
                        App.TEXT_COLOR
                        )
                else:
                    self._message.text = word
                    self._message.text_color = (
                        App.FOUND_COLOR
                        )
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
                    letter.highlight2 = App.FOUND_COLOR
                    letter.border = False
                    letter.render()
            else:
                self._message.text = word
                self._message.text_color = App.UNTHEME_COLOR
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
            self._message.text = info
            self._message.text_color = App.TEXT_COLOR
            self._message.render()
        else:
            i, b = info
            _, strand = self._game.answers()[i]
            positions = strand.positions()
            first_last = (positions[0], positions[-1])
            for pos in positions:
                position = (pos.r, pos.c)
                letter = self._letters_lookup[position]
                letter.highlight2 = App.HINT_COLOR
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
                letter.highlight1 = App.SELECT_COLOR
                letter.render()
            self._message.text = (
                self._game.board().evaluate_strand(new)
                )
            self._message.text_color = App.SELECT_COLOR
            self._message.render()
        self._select = new


    def _founder(self) -> None:
        """ show the number of words left in a message """
        if self._game.game_over():
            return
        left = (
            len(self._game.answers())
            - len(self._game.found_strands())
            )
        self._message.text = (
            App.MESSAGE_FOUND.format(left = left)
            )
        self._message.text_color = App.TEXT_COLOR
        self._message.render()


    # DISPLAY DRAWING METHODS

    def _render(self) -> None:
        """ render the display """
        self._canvas.fill(App.CANVAS_COLOR)
        self._draw_borders()
        for strand in self._game.found_strands():
            self._connect(strand, App.FOUND_COLOR)
        if self._select is not None:
            self._connect(self._select, App.SELECT_COLOR)
        self._letters.draw(self._canvas)
        self._theme.draw(self._canvas)
        self._message.draw(self._canvas)
        self._hint.draw(self._canvas)
        self._found.draw(self._canvas)
        pygame.display.update()


    def _draw_borders(self) -> None:
        """
        draw the borders (helper function for _render)
        """
        _, xb, yb = self._adj
        w, h = self._canvas.get_size()
        pygame.draw.rect(
            self._canvas,
            App.BORDER_COLOR,
            pygame.Rect(0, 0, w, yb)
            )
        pygame.draw.rect(
            self._canvas,
            App.BORDER_COLOR,
            pygame.Rect(0, 0, xb, h)
            )
        pygame.draw.rect(
            self._canvas,
            App.BORDER_COLOR,
            pygame.Rect(0, h - yb, w, yb)
            )
        pygame.draw.rect(
            self._canvas,
            App.BORDER_COLOR,
            pygame.Rect(w - xb, 0, xb, h)
            )


    def _connect(
        self,
        strand: StrandBase,
        color: pygame.Color
        ) -> None:
        """
        draw the connections between letters of a
        strand (helper method for _render)

        Inputs:
            strand (Strand): the strand to draw
                connections for
            color (pygame.Color): the color to draw
                the connections with
        """
        radius = round(
            App.CONNECT_SCALE
            * self._adj.a
            * min(App.GRID_SIZE)
            )
        def connect(
            positions: list[PosBase]
            ) -> tuple[int, int]:
            """
            recursively draw lines between the centers
            of the letters at each position given

            Input:
                positions (list[PosBase]): a list of
                    positions on the board to draw
                    lines between
            Output (tuple[int, int]):
                - The x, y center coordinates of the
                    letter sprite corresponding to the
                    last position in the list.
            """
            if len(positions) == 1:
                letter = self._letters_lookup[
                    positions[0].r, positions[0].c
                    ]
                return letter.rect.center
            start = connect(positions[:-1])
            stop = connect(positions[-1:])
            pygame.draw.line(
                self._canvas,
                color,
                start,
                stop,
                radius
                )
            return stop
        connect(strand.positions())
