"""
Strands TUI Implementation
"""
# Vedat

import curses
from base import StrandsGameBase, BoardBase
from stubs import StrandsGameStub, StrandStub, PosStub
from finals.pos import Pos

STRAND_COLORS = [
    curses.COLOR_CYAN,
    curses.COLOR_GREEN,
    curses.COLOR_YELLOW,
    curses.COLOR_MAGENTA,
    curses.COLOR_RED,
    curses.COLOR_BLUE,
]

CELL_WIDTH = 3
ROW_HEIGHT = 2
BOARD_START_ROW = 3
CONTROLS = "[q] Quit  [Enter] Submit  [h] Hint  [Esc] Clear"

CARDINAL_KEYS = frozenset([
    curses.KEY_UP, curses.KEY_DOWN,
    curses.KEY_LEFT, curses.KEY_RIGHT,
])

SHIFT_KEYS = frozenset([curses.KEY_SLEFT, curses.KEY_SRIGHT])

SHIFT_PENDING: dict[int, str] = {
    curses.KEY_SR: "N",
    curses.KEY_SF: "S",
}


def build_found_map(game: StrandsGameBase) -> dict[tuple[int, int], int]:
    """Map (row, col) -> strand index for all found strand positions."""
    result: dict[tuple[int, int], int] = {}
    for i, strand in enumerate(game.found_strands()):
        for pos in strand.positions():
            result[(pos.r, pos.c)] = i
    return result


def draw_board(
    stdscr: curses.window,
    board: BoardBase,
    found_map: dict[tuple[int, int], int],
    start_row: int,
) -> None:
    """Draw the letter grid with found strands colored."""
    for r in range(board.num_rows()):
        for c in range(board.num_cols()):
            letter = board.get_letter(Pos(r, c)).upper()
            scr_row = start_row + r * ROW_HEIGHT
            scr_col = c * CELL_WIDTH
            if (r, c) in found_map:
                attr = curses.color_pair(found_map[(r, c)] + 1) | curses.A_BOLD
                stdscr.addstr(scr_row, scr_col, f" {letter} ", attr)
            else:
                stdscr.addstr(scr_row, scr_col, f" {letter} ")


def draw(stdscr: curses.window, game: StrandsGameBase) -> None:
    """Redraw the entire screen."""
    stdscr.clear()
    board = game.board()
    found_map = build_found_map(game)

    stdscr.addstr(0, 0, f"Theme: {game.theme()}", curses.A_BOLD)

    found = len(game.found_strands())
    total = len(game.answers())
    meter = game.hint_meter()
    threshold = game.hint_threshold()
    info = f"Words: {found}/{total}  Hints: {meter}/{threshold}"
    stdscr.addstr(1, 0, info)

    draw_board(stdscr, board, found_map, BOARD_START_ROW)

    controls_row = BOARD_START_ROW + board.num_rows() * ROW_HEIGHT + 1
    stdscr.addstr(controls_row, 0, CONTROLS)
    stdscr.refresh()


def handle_key(
    key: int,
    game: StrandsGameBase,
    pending: str | None,
) -> tuple[bool, str | None]:
    """Handle a keypress. Returns (should_quit, new_pending_shift)."""
    if key == ord('q'):
        return True, None

    if key in (ord('\n'), curses.KEY_ENTER, 10, 13):
        game.submit_strand(StrandStub(PosStub(0, 0), []))
        return False, None

    if key == ord('h'):
        game.use_hint()
        return False, None

    if key in SHIFT_PENDING:
        return False, SHIFT_PENDING[key]

    if key == 27 or key in CARDINAL_KEYS or key in SHIFT_KEYS:
        # M2: SHIFT_KEYS use pending + key to resolve NW/NE/SW/SE
        return False, None

    return False, pending


def main(stdscr: curses.window) -> None:
    """Main TUI event loop."""
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    for i, color in enumerate(STRAND_COLORS):
        curses.init_pair(i + 1, color, -1)

    game: StrandsGameBase = StrandsGameStub("boards/cs-142.txt", 3)
    pending_shift: str | None = None

    while True:
        draw(stdscr, game)
        key = stdscr.getch()
        quit_game, pending_shift = handle_key(key, game, pending_shift)
        if quit_game:
            break


if __name__ == "__main__":
    curses.wrapper(main)
