"""
Strands TUI Implementation
"""
# Vedat

import sys
import curses
from base import StrandsGameBase, BoardBase, Step, PosBase
from fakes import StrandsGameFake
from finals.pos import Pos
from finals.strand import Strand

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
BOARD_START_ROW = 4
NAV_RULES = "Nav: arrows=NSEW  Shift+Up+Left/Right=NW/NE  Shift+Down=SW/SE"
CONTROLS = "[q] Quit  [Enter] Select/Submit  [h] Hint  [Esc] Clear"
NUM_COLORS = len(STRAND_COLORS)

PAIR_SELECTION = NUM_COLORS + 1
PAIR_HINT = NUM_COLORS + 2
PAIR_HINT_ENDS = NUM_COLORS + 3

CARDINAL_STEPS: dict[int, Step] = {
    curses.KEY_UP: Step.N,
    curses.KEY_DOWN: Step.S,
    curses.KEY_LEFT: Step.W,
    curses.KEY_RIGHT: Step.E,
}

SHIFT_PENDING: dict[int, str] = {
    curses.KEY_SR: "N",
    curses.KEY_SF: "S",
}

INTERCARDINAL: dict[tuple[str, int], Step] = {
    ("N", curses.KEY_SLEFT): Step.NW,
    ("N", curses.KEY_SRIGHT): Step.NE,
    ("S", curses.KEY_SLEFT): Step.SW,
    ("S", curses.KEY_SRIGHT): Step.SE,
}


def build_found_map(
    game: StrandsGameBase,
) -> dict[tuple[int, int], int]:
    """Map (row, col) -> strand index for all found strand positions."""
    result: dict[tuple[int, int], int] = {}
    for i, strand in enumerate(game.found_strands()):
        for pos in strand.positions():
            result[(pos.r, pos.c)] = i
    return result


def build_hint_sets(
    game: StrandsGameBase,
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """Return (hint_positions, hint_endpoints) sets for active hint."""
    hint = game.active_hint()
    if hint is None:
        return set(), set()
    i, show_ends = hint
    positions = game.answers()[i][1].positions()
    hint_set = {(p.r, p.c) for p in positions}
    if not show_ends:
        return hint_set, set()
    ends = {
        (positions[0].r, positions[0].c),
        (positions[-1].r, positions[-1].c),
    }
    return hint_set, ends


def cell_attr(
    r: int,
    c: int,
    found_map: dict[tuple[int, int], int],
    sel_set: set[tuple[int, int]],
    hints: tuple[set[tuple[int, int]], set[tuple[int, int]]],
) -> int:
    """Return display attribute for a board cell."""
    hint_set, hint_ends = hints
    if (r, c) in sel_set:
        return curses.color_pair(PAIR_SELECTION) | curses.A_BOLD
    if (r, c) in hint_ends:
        return curses.color_pair(PAIR_HINT_ENDS) | curses.A_BOLD
    if (r, c) in hint_set:
        return curses.color_pair(PAIR_HINT)
    if (r, c) in found_map:
        idx = found_map[(r, c)] % NUM_COLORS
        return curses.color_pair(idx + 1) | curses.A_BOLD
    return 0


def draw_connection(
    stdscr: curses.window,
    pos1: PosBase,
    pos2: PosBase,
    attr: int,
) -> None:
    """Draw a connector between two adjacent board positions."""
    r1, c1 = pos1.r, pos1.c
    r2, c2 = pos2.r, pos2.c
    top_r = min(r1, r2)
    left_c = min(c1, c2)
    if r1 == r2:
        scr_row = BOARD_START_ROW + r1 * ROW_HEIGHT
        stdscr.addstr(scr_row, left_c * CELL_WIDTH + 2, '-', attr)
    elif c1 == c2:
        scr_row = BOARD_START_ROW + top_r * ROW_HEIGHT + 1
        stdscr.addstr(scr_row, c1 * CELL_WIDTH + 1, '|', attr)
    elif (r2 - r1) * (c2 - c1) > 0:
        scr_row = BOARD_START_ROW + top_r * ROW_HEIGHT + 1
        stdscr.addstr(scr_row, left_c * CELL_WIDTH + 2, '\\', attr)
    else:
        scr_row = BOARD_START_ROW + top_r * ROW_HEIGHT + 1
        stdscr.addstr(scr_row, left_c * CELL_WIDTH + 2, '/', attr)


def draw_strand_connections(
    stdscr: curses.window,
    positions: list[PosBase],
    attr: int,
) -> None:
    """Draw connectors between consecutive positions in a strand."""
    for i in range(len(positions) - 1):
        draw_connection(stdscr, positions[i], positions[i + 1], attr)


def draw_found_connections(
    stdscr: curses.window,
    game: StrandsGameBase,
) -> None:
    """Draw connections for all found strands."""
    for i, strand in enumerate(game.found_strands()):
        attr = curses.color_pair(i % NUM_COLORS + 1) | curses.A_BOLD
        draw_strand_connections(stdscr, strand.positions(), attr)


def _draw_board_cells(
    stdscr: curses.window,
    board: BoardBase,
    game: StrandsGameBase,
    sel_set: set[tuple[int, int]],
    cursor: PosBase,
) -> None:
    """Draw all board cells with appropriate colors and cursor."""
    found_map = build_found_map(game)
    hints = build_hint_sets(game)
    for r in range(board.num_rows()):
        for c in range(board.num_cols()):
            letter = board.get_letter(Pos(r, c)).upper()
            scr_row = BOARD_START_ROW + r * ROW_HEIGHT
            scr_col = c * CELL_WIDTH
            attr = cell_attr(r, c, found_map, sel_set, hints)
            if (r, c) == (cursor.r, cursor.c):
                attr = attr | curses.A_REVERSE
            stdscr.addstr(scr_row, scr_col, f" {letter} ", attr)


def draw_board(
    stdscr: curses.window,
    board: BoardBase,
    game: StrandsGameBase,
    cursor: PosBase,
    selection: list[PosBase],
) -> None:
    """Draw the letter grid with strands, selection, hints, cursor."""
    sel_set = {(p.r, p.c) for p in selection}
    _draw_board_cells(stdscr, board, game, sel_set, cursor)
    draw_found_connections(stdscr, game)
    if len(selection) > 1:
        s_attr = curses.color_pair(PAIR_SELECTION) | curses.A_BOLD
        draw_strand_connections(stdscr, selection, s_attr)
    hint = game.active_hint()
    if hint is not None:
        h_pos = game.answers()[hint[0]][1].positions()
        h_attr = curses.color_pair(PAIR_HINT)
        draw_strand_connections(stdscr, h_pos, h_attr)


def draw(
    stdscr: curses.window,
    game: StrandsGameBase,
    cursor: PosBase,
    selection: list[PosBase],
    status: str,
) -> None:
    """Redraw the entire screen."""
    stdscr.clear()
    board = game.board()
    stdscr.addstr(0, 0, NAV_RULES)
    stdscr.addstr(1, 0, f"Theme: {game.theme()}", curses.A_BOLD)
    found = len(game.found_strands())
    total = len(game.answers())
    meter = game.hint_meter()
    threshold = game.hint_threshold()
    info = f"Words: {found}/{total}  Hints: {meter}/{threshold}"
    stdscr.addstr(2, 0, info)
    if status:
        stdscr.addstr(3, 0, status)
    draw_board(stdscr, board, game, cursor, selection)
    controls_row = BOARD_START_ROW + board.num_rows() * ROW_HEIGHT + 1
    stdscr.addstr(controls_row, 0, CONTROLS)
    stdscr.refresh()


def _draw_show_cells(
    stdscr: curses.window,
    board: BoardBase,
    all_map: dict[tuple[int, int], int],
) -> None:
    """Draw board cells for show mode with strand colors."""
    for r in range(board.num_rows()):
        for c in range(board.num_cols()):
            letter = board.get_letter(Pos(r, c)).upper()
            scr_row = BOARD_START_ROW + r * ROW_HEIGHT
            scr_col = c * CELL_WIDTH
            attr = 0
            if (r, c) in all_map:
                attr = (
                    curses.color_pair(all_map[(r, c)] % NUM_COLORS + 1)
                    | curses.A_BOLD
                )
            stdscr.addstr(scr_row, scr_col, f" {letter} ", attr)


def draw_show(stdscr: curses.window, game: StrandsGameBase) -> None:
    """Draw all answer strands for show mode."""
    stdscr.clear()
    board = game.board()
    stdscr.addstr(0, 0, f"Theme: {game.theme()}", curses.A_BOLD)
    stdscr.addstr(1, 0, "Show mode  [q] Quit")
    all_map: dict[tuple[int, int], int] = {}
    for i, (_, strand) in enumerate(game.answers()):
        for pos in strand.positions():
            all_map[(pos.r, pos.c)] = i
    _draw_show_cells(stdscr, board, all_map)
    for i, (_, strand) in enumerate(game.answers()):
        attr = curses.color_pair(i % NUM_COLORS + 1) | curses.A_BOLD
        draw_strand_connections(stdscr, strand.positions(), attr)
    controls_row = BOARD_START_ROW + board.num_rows() * ROW_HEIGHT + 1
    stdscr.addstr(controls_row, 0, "[q] Quit")
    stdscr.refresh()


def try_move(
    cursor: PosBase,
    step: Step,
    board: BoardBase,
) -> PosBase:
    """Move cursor one step if within bounds, else return current."""
    new_pos = cursor.take_step(step)
    if 0 <= new_pos.r < board.num_rows():
        if 0 <= new_pos.c < board.num_cols():
            return new_pos
    return cursor


def update_selection(
    selection: list[PosBase],
    new_pos: PosBase,
) -> list[PosBase]:
    """Extend or truncate selection based on cursor movement."""
    for i, pos in enumerate(selection):
        if pos == new_pos:
            return selection[:i + 1]
    if selection and selection[-1].is_adjacent_to(new_pos):
        return selection + [new_pos]
    return selection


def selection_to_strand(selection: list[PosBase]) -> Strand:
    """Build a Strand from a list of positions."""
    steps = [
        selection[i].step_to(selection[i + 1])
        for i in range(len(selection) - 1)
    ]
    return Strand(selection[0], steps)


def get_step(key: int, pending: str | None) -> Step | None:
    """Return movement step from key and pending shift state."""
    if key in CARDINAL_STEPS:
        return CARDINAL_STEPS[key]
    if pending is not None and (pending, key) in INTERCARDINAL:
        return INTERCARDINAL[(pending, key)]
    return None


def format_hint(result: tuple[int, bool] | str) -> str:
    """Format hint result as a status message."""
    if isinstance(result, str):
        return result
    _, show_ends = result
    return "Hint: endpoints shown!" if show_ends else "Hint active!"


def _is_partial_answer(
    selection: list[PosBase],
    game: StrandsGameBase,
) -> bool:
    """Return True if selection is a strict subset of any answer strand."""
    submitted = {(p.r, p.c) for p in selection}
    for _, ans_strand in game.answers():
        ans_pos = {(p.r, p.c) for p in ans_strand.positions()}
        if submitted < ans_pos:
            return True
    return False


def _handle_enter(
    game: StrandsGameBase,
    cursor: PosBase,
    selection: list[PosBase],
) -> tuple[PosBase, list[PosBase], str | None, str]:
    """Handle Enter: start selection at cursor or submit strand."""
    if not selection:
        return cursor, [cursor], None, ""
    if _is_partial_answer(selection, game):
        return cursor, selection, None, "Keep selecting..."
    strand = selection_to_strand(selection)
    result = game.submit_strand(strand)
    if isinstance(result, tuple):
        word, is_theme = result
        msg = f"Found: {word.upper()}!" if is_theme else f"Word: {word}"
    else:
        msg = str(result)
    return cursor, [], None, msg


def handle_key(
    key: int,
    game: StrandsGameBase,
    cursor: PosBase,
    selection: list[PosBase],
    pending: str | None,
) -> tuple[bool, PosBase, list[PosBase], str | None, str]:
    """Handle a keypress. Returns (quit, cursor, selection, pending, status)."""
    new_pending = pending
    new_status = ""
    new_cursor = cursor
    new_sel = selection
    quit_game = False
    if key == ord('q'):
        quit_game = True
        new_pending = None
    elif key == 27:
        new_sel = []
        new_pending = None
    elif key in (ord('\n'), curses.KEY_ENTER, 10, 13):
        new_cursor, new_sel, new_pending, new_status = _handle_enter(
            game, cursor, selection
        )
    elif key == ord('h'):
        new_status = format_hint(game.use_hint())
    elif key in SHIFT_PENDING:
        new_pending = SHIFT_PENDING[key]
    else:
        step = get_step(key, pending)
        if step is not None:
            new_cursor = try_move(cursor, step, game.board())
            new_sel = update_selection(new_sel, new_cursor)
            new_pending = None
    return quit_game, new_cursor, new_sel, new_pending, new_status


def show_mode(stdscr: curses.window, game: StrandsGameBase) -> None:
    """Display all answer strands. Press q to exit."""
    draw_show(stdscr, game)
    while stdscr.getch() != ord('q'):
        pass


def play_mode(stdscr: curses.window, game: StrandsGameBase) -> None:
    """Main play event loop."""
    cursor: PosBase = Pos(0, 0)
    selection: list[PosBase] = []
    pending: str | None = None
    status = ""
    while not game.game_over():
        draw(stdscr, game, cursor, selection, status)
        key = stdscr.getch()
        quit_game, cursor, selection, pending, status = handle_key(
            key, game, cursor, selection, pending
        )
        if quit_game:
            break
    if game.game_over():
        draw(stdscr, game, cursor, selection, "You won! Press q to exit.")
        while stdscr.getch() != ord('q'):
            pass


def main(stdscr: curses.window) -> None:
    """Main curses entry point."""
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    for i, color in enumerate(STRAND_COLORS):
        curses.init_pair(i + 1, color, -1)
    curses.init_pair(PAIR_SELECTION, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_HINT, curses.COLOR_YELLOW, -1)
    curses.init_pair(PAIR_HINT_ENDS, curses.COLOR_RED, -1)
    game: StrandsGameBase = StrandsGameFake(sys.argv[2], 3)
    if sys.argv[1] == "show":
        show_mode(stdscr, game)
    else:
        play_mode(stdscr, game)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("play", "show"):
        print("Usage: python3 tui.py [play|show] <gamefile>")
        sys.exit(1)
    curses.wrapper(main)
