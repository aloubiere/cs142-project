"""
Strands GUI Implementation
"""
# Amber

import sys
from typing import NamedTuple
from copy import deepcopy
from numpy import ndindex
import pygame
from base import (
    StrandBase, StrandsGameBase, PosBase
    )
from strands import Pos, Strand, StrandsGame
from gui_files.sprites import (
    TextSprite, LetterSprite, MeterSprite, Specs, GridSpecs
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
    # between and around info sprites in the pygame window
    INFO_ELEMENT_BUFFER: tuple[float, float] = (7/8, 3/4)

    # used by StrandsGUI to scale sprites to add space
    # between and around letter sprites in the pygame
    # window
    GRID_ELEMENT_BUFFER: tuple[float, float] = (4/5, 4/5)

    # the starting text2 for the message sprite
    MESSAGE_START: str = "Good luck!"

    # the winning text2 for the message sprite
    MESSAGE_WIN: str = "You win!"

    # the text2 if submitting nothing for the message sprite
    MESSAGE_EMPTY: str = "Nothing selected"

    # the text2 if clicking on the found sprite
    MESSAGE_FOUND: str = "Only {left} left!"

    # the default aspect ratio for the hint sprite
    HINT_AR: float = 3.5

    # the text2 for the hint sprite if it is a Text object
    HINT_TEXT: str = "HINT"

    # the text2 for the hint sprite if it is a Meter object
    HINT_METER: str = "HINT"

    # the text2 for the found sprite if it is a Text object
    FOUND_TEXT: str = "Found?"

    # the text2 for the found sprite if it is a Meter object
    FOUND_METER: str = "Found {meter}/{threshold}"

    # the scaling factor for the strand connection lines
    CONNECT_SCALE: float = 1/3

    # the background color of the canvas
    CANVAS_COLOR: pygame.Color = pygame.Color("white")

    # the default color of text2
    TEXT_COLOR: pygame.Color = pygame.Color("black")

    # the color used to show selected strands
    SELECT_COLOR: pygame.Color = pygame.Color("lightgray")

    # the color used to show dictionary words when found
    OTHER_COLOR: pygame.Color = pygame.Color("black")

    # the color used to show active hints
    HINT_COLOR: pygame.Color = pygame.Color("lavender")

    # the color used to show found words
    FOUND_COLOR: pygame.Color = pygame.Color("lightskyblue")

    # the color of the border around the board
    BORDER_COLOR: pygame.Color = pygame.Color("snow2")


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
    _selection: StrandBase | None

    # a list of all the letters on the board
    # decided to use a list because type checking
    # does not work well for pygame sprite groups
    _letters: list[LetterSprite]

    # used for looking up letters by their position
    _letters_lookup: dict[tuple[int, int], LetterSprite]

    # the hint button sprite
    _hint: MeterSprite | TextSprite

    # a sprite for displaying game messages
    _message: TextSprite

    # a sprite for displaying the game progress
    # the number of theme words found and the total
    # to find
    _found: MeterSprite | TextSprite

    # a sprite for displaying the game theme
    _theme: TextSprite


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
                "The argument `mode` must be boolean. "
                f"The type is {type(mode)}."
                )
        if not isinstance(game, str):
            raise TypeError(
                "The argument `game` must be a string. "
                f"The type is {type(game)}."
                )
        if hint_threshold is not None:
            if not isinstance(hint_threshold, int):
                raise TypeError(
                    "The argument `hint_threshold` must "
                    "be a nonnegative integer. The type "
                    f"is {type(hint_threshold)}."
                    )
            if hint_threshold < 0:
                raise ValueError(
                    "The argument `hint_threshold` must "
                    "be a nonnegative integer. The value "
                    f"is {hint_threshold}."
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
        self._selection = None
        self._generate_sprites()
        if mode:
            for _, strand in self._game.answers():
                self._selection = strand
                self._submit()


    # SIZING METHODS

    def _size(
        self,
        size: tuple[int, int] | None = None
        ) -> tuple[int, int]:
        """
        scale the canvas and/or board and update the
        attribute `_adj` accordingly

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
        border are saved in the `_adj` attribute, in that
        order.

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


    def _spec_infos(self) -> InfoSpecs:
        """
        calculate the specs for the info sprites

        Returns (InfoSpecs):
            - The sizes and positions for the info sprites
              as Specs objects in an InfoSpecs object.
        """
        canvas_w, canvas_h = self._canvas.get_size()
        scale_w, scale_h = App.INFO_ELEMENT_BUFFER
        # shared header and footer values
        max_w = max(1/2 * (canvas_w - 2 * self._adj.xb), 0)
        left_x = round(self._adj.xb + 1/2 * max_w)
        right_x = round(self._adj.xb + 3/2 * max_w)
        nonhint_w = round(scale_w * max_w)
        # header specific
        header_h = self._adj.a * App.HEADER
        header_y = round(self._adj.yb + 1/2 * header_h)
        header_h = round(scale_h * header_h)
        # footer specific
        footer_h = self._adj.a * App.FOOTER
        footer_y = round(
            canvas_h - self._adj.yb - 1/2 * footer_h
            )
        footer_h = round(scale_h * footer_h)
        hint_w = min(
            nonhint_w,
            round(scale_w * App.HINT_AR * footer_h)
            )

        return InfoSpecs(
            Specs(left_x, header_y, nonhint_w, header_h),
            Specs(right_x, header_y, nonhint_w, header_h),
            Specs(left_x, footer_y, hint_w, footer_h),
            Specs(right_x, footer_y, nonhint_w, footer_h)
            )


    def _gridspec_letters(self) -> GridSpecs:
        """
        calculate the grid specs for the letter sprites

        Returns (GridSpecs):
            - A GridSpecs object containing the values
              needed to calculate the size and position
              of each letter based on its position on
              the grid
        """
        a, xb, yb = self._adj
        grid_x, grid_y = (a * n for n in App.GRID_SIZE)
        scale_x, scale_y = App.GRID_ELEMENT_BUFFER
        offset =  (xb, round(yb + a * App.HEADER))
        spacing = (round(grid_x), round(grid_y))
        size = (
            round(scale_x * grid_x),
            round(scale_y * grid_y)
            )
        return GridSpecs(offset, spacing, size)


    # SPRITE MANAGEMENT METHODS

    def _generate_sprites(self) -> None:
        """ generate all sprites """
        # generate letter sprites
        self._letters_lookup = {}
        self._letters = []
        letter_gridspecs = self._gridspec_letters()
        for pos in ndindex((
            self._game.board().num_rows(),
            self._game.board().num_cols()
            )):
            ch = self._game.board().get_letter(Pos(*pos))
            letter = LetterSprite(
                pos, ch, letter_gridspecs
                )
            letter.render()
            self._letters.append(letter)
            self._letters_lookup[pos] = letter

        # generate info sprites
        specs = self._spec_infos()
        ## generate theme
        self._theme = TextSprite(
            self._game.theme(), specs.theme
            )
        self._theme.render()
        ## generate message
        self._message = TextSprite(
            App.MESSAGE_START,
            specs.message
            )
        self._message.render()
        ## generate hint
        if self._game.hint_threshold() <= 0:
            self._hint = TextSprite(
                App.HINT_TEXT, specs.hint
                )
            self._hint.container.border = True
        else:
            self._hint = MeterSprite(
                App.HINT_METER,
                specs.hint,
                self._game.hint_threshold(),
                True
                )
            self._hint.container.border = True
        self._hint.render()
        ## generate found
        if len(self._game.answers()) == 0:
            self._found = TextSprite(
                App.FOUND_TEXT, specs.found
                )
        else:
            self._found = MeterSprite(
                App.FOUND_METER,
                specs.found,
                len(self._game.answers())
                )
        self._found.render()


    def _update_sprites(self) -> None:
        """ update all sprites after a resizing """
        letter_gridspecs = self._gridspec_letters()
        for letter in self._letters:
            letter.resize(letter_gridspecs)
            letter.render()
        specs = self._spec_infos()
        self._hint.resize(specs.hint)
        self._hint.render()
        self._found.resize(specs.found)
        self._found.render()
        self._theme.resize(specs.theme)
        self._theme.render()
        self._message.resize(specs.message)
        self._message.render()


    # USER INTERACTION METHODS

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
            self._submit()
        elif key == pygame.K_ESCAPE:
            self._deselect()
        elif key == pygame.K_h:
            self._use_hint()
        self._render()


    def _click(self, x: int, y: int) -> None:
        """ process a mouse click at the position given """
        if self._hint.rect.collidepoint(x, y):
            self._use_hint()
        elif self._found.rect.collidepoint(x, y):
            self._show_progress()
        else:
            for letter in self._letters:
                if not letter.rect.collidepoint(x, y):
                    continue
                self._select(Pos(*letter.position), False)
                break
        self._render()


    def _selecting(self, x: int, y: int) -> None:
        """ process mouse dragging at the position given """
        for letter in self._letters:
            if letter.rect.collidepoint(x, y):
                self._select(Pos(*letter.position), True)
                break
        self._render()


    def _selected(self) -> None:
        """ process the end of mouse dragging """
        if self._selection is not None:
            if len(self._selection.positions()) == 1:
                self._deselect()
            else:
                self._submit()
            self._render()


    # GAME FUNCTIONALITY METHODS

    def _submit(self) -> None:
        """ submit a strand """
        if self._game.game_over():
            return
        if self._selection is None:
            self._message.text.text = App.MESSAGE_EMPTY
            self._message.text.color = App.TEXT_COLOR
            self._message.render()
            return
        info = self._game.submit_strand(self._selection)
        self._deselect()
        if isinstance(info, str):
            self._message.text.text = info
            self._message.text.color = App.TEXT_COLOR
            self._message.render()
        else:
            word, is_theme = info
            if is_theme:
                if self._game.game_over():
                    self._message.text.text = (
                        App.MESSAGE_WIN
                        )
                    self._message.text.color = (
                        App.TEXT_COLOR
                        )
                else:
                    self._message.text.text = word
                    self._message.text.color = (
                        App.FOUND_COLOR
                        )
                self._message.render()
                if isinstance(self._found, MeterSprite):
                    self._found.remeter(
                        len(self._game.found_strands())
                        )
                    self._found.render()
                strand = self._game.found_strands()[-1]
                for pos in strand.positions():
                    position = (pos.r, pos.c)
                    letter = self._letters_lookup[position]
                    letter.container.fill = True
                    letter.container.fill_color = (
                        App.FOUND_COLOR
                        )
                    for container in letter.containers:
                        container.border = False
                    letter.render()
            else:
                self._message.text.text = word
                self._message.text.color = App.OTHER_COLOR
                self._message.render()
                if isinstance(self._hint, MeterSprite):
                    self._hint.remeter(
                        self._game.hint_meter()
                        )
                    self._hint.render()


    def _use_hint(self) -> None:
        """ use a hint """
        if self._game.game_over():
            return
        info = self._game.use_hint()
        if isinstance(info, str):
            self._message.text_override()
            self._message.text.text = info
            self._message.text.color = App.TEXT_COLOR
            self._message.render()
        else:
            i, b = info
            _, strand = self._game.answers()[i]
            positions = strand.positions()
            first_last = (positions[0], positions[-1])
            for pos in positions:
                position = (pos.r, pos.c)
                letter = self._letters_lookup[position]
                letter.containers[0].fill = True
                letter.containers[0].fill_color = (
                    App.HINT_COLOR
                    )
                if b and pos in first_last:
                    for container in letter.containers:
                        container.border = True
                letter.render()
            if isinstance(self._hint, MeterSprite):
                self._hint.remeter(self._game.hint_meter())
                self._hint.render()


    def _deselect(self) -> None:
        """ deselect a strand """
        if self._selection is None:
            return
        for pos_ in self._selection.positions():
            position = (pos_.r, pos_.c)
            letter = self._letters_lookup[position]
            letter.container_override()
            letter.render()
        self._selection = None
        self._message.text_override()
        self._message.render()


    def _select(
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
        if self._selection is None:
            new = Strand(pos, [])
        else:
            *positions, last = self._selection.positions()
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
                    self._submit()
                    return
            # backtrack the selection to the given pos
            elif pos in positions:
                i = positions.index(pos)
                new = Strand(
                    self._selection.start,
                    self._selection.steps[:i]
                    )
            # extend the selection to the given pos
            elif pos.is_adjacent_to(last):
                new = Strand(
                    self._selection.start,
                    self._selection.steps
                        + [last.step_to(pos)]
                    )
            else:
                new = None

        # update letter sprites
        self._deselect() # clear the previous render first
        if new is not None:
            for pos_ in new.positions():
                position = (pos_.r, pos_.c)
                letter = self._letters_lookup[position]
                letter.container = deepcopy(
                    letter.container
                    )
                letter.container.fill = True
                letter.container.fill_color = (
                    App.SELECT_COLOR
                    )
                letter.render()
            self._message.text = deepcopy(
                self._message.text
                )
            self._message.text.text = (
                self._game.board().evaluate_strand(new)
                )
            self._message.text.color = App.SELECT_COLOR
            self._message.render()
        self._selection = new


    def _show_progress(self) -> None:
        """ show the number of words left in a message """
        if self._game.game_over():
            return
        left = (
            len(self._game.answers())
            - len(self._game.found_strands())
            )
        self._message.text_override()
        self._message.text.text = (
            App.MESSAGE_FOUND.format(left = left)
            )
        self._message.text.color = App.TEXT_COLOR
        self._message.render()


    # DISPLAY DRAWING METHODS

    def _render(self) -> None:
        """ render the display """
        self._canvas.fill(App.CANVAS_COLOR)
        self._draw_borders()
        for strand in self._game.found_strands():
            self._connect(strand, App.FOUND_COLOR)
        if self._selection is not None:
            self._connect(self._selection, App.SELECT_COLOR)
        for letter in self._letters:
            letter.draw(self._canvas)
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
