"""
Strands TUI Implementation
"""
# Vedat

import curses
from base import StrandsGameBase
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


def build_found_map(game: StrandsGameBase) -> dict[tuple[int, int], int]:
    """Map (row, col) -> strand index for all found strand positions."""
    result: dict[tuple[int, int], int] = {}
    for i, strand in enumerate(game.found_strands()):
        for pos in strand.positions():
            result[(pos.r, pos.c)] = i
    return result


def draw(stdscr: curses.window, game: StrandsGameBase) -> None:
    """Redraw the entire screen."""
    stdscr.clear()
    board = game.board()
    found_map = build_found_map(game)

    row = 0

    stdscr.addstr(row, 0, f"Theme: {game.theme()}", curses.A_BOLD)
    row += 1

    found_count = len(game.found_strands())
    total = len(game.answers())
    meter = game.hint_meter()
    threshold = game.hint_threshold()
    stdscr.addstr(row, 0, f"Words: {found_count}/{total}   Hints: {meter}/{threshold}")
    row += 2

    board_start = row

    for r in range(board.num_rows()):
        col_x = 0
        for c in range(board.num_cols()):
            letter = board.get_letter(Pos(r, c)).upper()
            screen_row = board_start + r * ROW_HEIGHT

            if (r, c) in found_map:
                pair = curses.color_pair(found_map[(r, c)] + 1)
                stdscr.addstr(screen_row, col_x, f" {letter} ", pair | curses.A_BOLD)
            else:
                stdscr.addstr(screen_row, col_x, f" {letter} ")

            col_x += CELL_WIDTH

    controls_row = board_start + board.num_rows() * ROW_HEIGHT + 1
    stdscr.addstr(controls_row, 0, "[q] Quit   [Enter] Submit   [h] Hint   [Esc] Clear")

    stdscr.refresh()


def main(stdscr: curses.window) -> None:
    """Main TUI event loop."""
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    for i, color in enumerate(STRAND_COLORS):
        curses.init_pair(i + 1, color, -1)

    game: StrandsGameBase = StrandsGameStub("boards/cs-142.txt", 3)

    # State for shifty 4-key navigation (M2)
    pending_shift: str | None = None

    while True:
        draw(stdscr, game)
        key = stdscr.getch()

        if key == ord('q'):
            break

        elif key in (ord('\n'), curses.KEY_ENTER, 10, 13):
            pending_shift = None
            game.submit_strand(StrandStub(PosStub(0, 0), []))

        elif key == ord('h'):
            pending_shift = None
            game.use_hint()

        elif key == 27:  # Escape
            pending_shift = None

        # Cardinal directions (M2: move cursor)
        elif key == curses.KEY_UP:
            pending_shift = None
        elif key == curses.KEY_DOWN:
            pending_shift = None
        elif key == curses.KEY_LEFT:
            pending_shift = None
        elif key == curses.KEY_RIGHT:
            pending_shift = None

        # Shifty 4-key: first key sets pending direction
        elif key == curses.KEY_SR:    # shift+up
            pending_shift = "N"
        elif key == curses.KEY_SF:    # shift+down
            pending_shift = "S"

        # Shifty 4-key: second key resolves intercardinal direction
        elif key == curses.KEY_SLEFT:
            if pending_shift == "N":
                pass  # M2: move cursor NW
            elif pending_shift == "S":
                pass  # M2: move cursor SW
            pending_shift = None

        elif key == curses.KEY_SRIGHT:
            if pending_shift == "N":
                pass  # M2: move cursor NE
            elif pending_shift == "S":
                pass  # M2: move cursor SE
            pending_shift = None

        else:
            pending_shift = None


if __name__ == "__main__":
    curses.wrapper(main)
