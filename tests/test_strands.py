"""
Milestone 1 QA tests for Strands game logic.
"""

import pytest

from base import BoardBase, PosBase, Step, StrandBase, StrandsGameBase
from strands import Board, Pos, Strand, StrandsGame


def test_inheritance() -> None:
    """
    Test that the concrete game logic classes inherit from the
    corresponding abstract base classes.
    """
    assert issubclass(Pos, PosBase)
    assert issubclass(Strand, StrandBase)
    assert issubclass(Board, BoardBase)
    assert issubclass(StrandsGame, StrandsGameBase)


def test_pos_take_step() -> None:
    """
    Test taking one step in each of the eight neighboring directions.
    """
    pos = Pos(10, 5)

    assert pos.take_step(Step.N) == Pos(9, 5)
    assert pos.take_step(Step.S) == Pos(11, 5)
    assert pos.take_step(Step.E) == Pos(10, 6)
    assert pos.take_step(Step.W) == Pos(10, 4)

    assert pos.take_step(Step.NW) == Pos(9, 4)
    assert pos.take_step(Step.NE) == Pos(9, 6)
    assert pos.take_step(Step.SW) == Pos(11, 4)
    assert pos.take_step(Step.SE) == Pos(11, 6)


def test_pos_step_to_success() -> None:
    """
    Test computing the step from one position to each of its
    eight neighboring positions.
    """
    pos = Pos(10, 5)

    assert pos.step_to(Pos(9, 5)) == Step.N
    assert pos.step_to(Pos(11, 5)) == Step.S
    assert pos.step_to(Pos(10, 6)) == Step.E
    assert pos.step_to(Pos(10, 4)) == Step.W

    assert pos.step_to(Pos(9, 4)) == Step.NW
    assert pos.step_to(Pos(9, 6)) == Step.NE
    assert pos.step_to(Pos(11, 4)) == Step.SW
    assert pos.step_to(Pos(11, 6)) == Step.SE


def test_pos_step_to_failure() -> None:
    """
    Test that step_to raises ValueError when positions are too far apart.
    """
    pos = Pos(10, 5)

    two_steps_away = [
        Pos(8, 5),
        Pos(12, 5),
        Pos(10, 7),
        Pos(10, 3),
        Pos(8, 3),
        Pos(8, 7),
        Pos(12, 3),
        Pos(12, 7),
    ]

    three_steps_away = [
        Pos(7, 5),
        Pos(13, 5),
        Pos(10, 8),
        Pos(10, 2),
        Pos(7, 2),
        Pos(13, 8),
    ]

    for other in two_steps_away + three_steps_away:
        with pytest.raises(ValueError):
            pos.step_to(other)


def test_strand_positions_straight_cardinal() -> None:
    """
    Test positions for strands moving in each cardinal direction.
    """
    north = Strand(Pos(5, 5), [Step.N, Step.N, Step.N, Step.N])
    south = Strand(Pos(5, 5), [Step.S, Step.S, Step.S, Step.S])
    east = Strand(Pos(5, 5), [Step.E, Step.E, Step.E, Step.E])
    west = Strand(Pos(5, 5), [Step.W, Step.W, Step.W, Step.W])

    assert north.positions() == [
        Pos(5, 5), Pos(4, 5), Pos(3, 5), Pos(2, 5), Pos(1, 5)
    ]
    assert south.positions() == [
        Pos(5, 5), Pos(6, 5), Pos(7, 5), Pos(8, 5), Pos(9, 5)
    ]
    assert east.positions() == [
        Pos(5, 5), Pos(5, 6), Pos(5, 7), Pos(5, 8), Pos(5, 9)
    ]
    assert west.positions() == [
        Pos(5, 5), Pos(5, 4), Pos(5, 3), Pos(5, 2), Pos(5, 1)
    ]


def test_strand_positions_straight_intercardinal() -> None:
    """
    Test positions for strands moving in each intercardinal direction.
    """
    northwest = Strand(Pos(5, 5), [Step.NW, Step.NW, Step.NW, Step.NW])
    northeast = Strand(Pos(5, 5), [Step.NE, Step.NE, Step.NE, Step.NE])
    southwest = Strand(Pos(5, 5), [Step.SW, Step.SW, Step.SW, Step.SW])
    southeast = Strand(Pos(5, 5), [Step.SE, Step.SE, Step.SE, Step.SE])

    assert northwest.positions() == [
        Pos(5, 5), Pos(4, 4), Pos(3, 3), Pos(2, 2), Pos(1, 1)
    ]
    assert northeast.positions() == [
        Pos(5, 5), Pos(4, 6), Pos(3, 7), Pos(2, 8), Pos(1, 9)
    ]
    assert southwest.positions() == [
        Pos(5, 5), Pos(6, 4), Pos(7, 3), Pos(8, 2), Pos(9, 1)
    ]
    assert southeast.positions() == [
        Pos(5, 5), Pos(6, 6), Pos(7, 7), Pos(8, 8), Pos(9, 9)
    ]

SLEEP_TIGHT_BOARD = [
    ["g", "u", "t", "i", "d", "m"],
    ["h", "a", "d", "a", "t", "e"],
    ["t", "r", "m", "n", "o", "i"],
    ["u", "o", "t", "i", "m", "e"],
    ["b", "e", "d", "s", "g", "u"],
    ["m", "i", "n", "m", "p", "l"],
    ["e", "n", "o", "a", "k", "r"],
    ["l", "a", "t", "s", "e", "a"],
]


def sleep_tight_answers() -> list[tuple[str, Strand]]:
    """
    Return the expected answers for boards/sleep-tight.txt.
    """
    return [
        ("mask", Strand(Pos(5, 3), [Step.S, Step.S, Step.NE])),
        ("earplugs", Strand(Pos(7, 4), [
            Step.E, Step.N, Step.NW, Step.E, Step.N, Step.W, Step.W
        ])),
        ("melatonin", Strand(Pos(5, 0), [
            Step.S, Step.S, Step.E, Step.E, Step.N, Step.N, Step.W, Step.S
        ])),
        ("meditation", Strand(Pos(0, 5), [
            Step.S, Step.NW, Step.W, Step.W, Step.SE,
            Step.E, Step.SE, Step.W, Step.W
        ])),
        ("mouthguard", Strand(Pos(2, 2), [
            Step.SW, Step.W, Step.N, Step.N, Step.N,
            Step.E, Step.S, Step.S, Step.NE
        ])),
        ("bedtime", Strand(Pos(4, 0), [
            Step.E, Step.E, Step.N, Step.E, Step.E, Step.E
        ])),
    ]


def sleep_tight_lines() -> list[str]:
    """
    Return a list of strings representing the sleep-tight game file.
    """
    return [
        '"Sleep tight"\n',
        "\n",
        "G U T I D M\n",
        "H A D A T E\n",
        "T R M N O I\n",
        "U O T I M E\n",
        "B E D S G U\n",
        "M I N M P L\n",
        "E N O A K R\n",
        "L A T S E A\n",
        "\n",
        "mask        6 4  s s ne\n",
        "earplugs    8 5  e n nw e n w w\n",
        "melatonin   6 1  s s e e n n w s\n",
        "meditation  1 6  s nw w w se e se w w\n",
        "mouthguard  3 3  sw w n n n e s s ne\n",
        "bedtime     5 1  e e n e e e\n",
        "\n",
        "https://www.nytimes.com/games/strands (4/27/2025)\n",
    ]


def test_load_game_sleep_tight_file() -> None:
    """
    Test loading boards/sleep-tight.txt from a filename.
    """
    game = StrandsGame("boards/sleep-tight.txt")

    assert game.theme() == '"Sleep tight"'
    assert game.board().num_rows() == 8
    assert game.board().num_cols() == 6
    assert game.answers() == sleep_tight_answers()

    for r, row in enumerate(SLEEP_TIGHT_BOARD):
        for c, expected_letter in enumerate(row):
            assert game.board().get_letter(Pos(r, c)) == expected_letter


def test_load_game_sleep_tight_variations() -> None:
    """
    Test that loading works with a list of strings and with acceptable
    whitespace and capitalization variations.
    """
    normal_lines = sleep_tight_lines()

    extra_spacing_lines = [
        '"Sleep tight"\n',
        "\n",
        "G   U T    I D M\n",
        "H A   D A T   E\n",
        "T R M N   O I\n",
        "U O T I M E\n",
        "B E D S G U\n",
        "M I N M P L\n",
        "E N O A K R\n",
        "L A T S E A\n",
        "\n",
        "mask 6 4 s s ne\n",
        "earplugs 8 5 e n nw e n w w\n",
        "melatonin 6 1 s s e e n n w s\n",
        "meditation 1 6 s nw w w se e se w w\n",
        "mouthguard 3 3 sw w n n n e s s ne\n",
        "bedtime 5 1 e e n e e e\n",
    ]

    capitalization_lines = [
        '"Sleep tight"\n',
        "\n",
        "g u t i d m\n",
        "h a d a t e\n",
        "t r m n o i\n",
        "u o t i m e\n",
        "b e d s g u\n",
        "m i n m p l\n",
        "e n o a k r\n",
        "l a t s e a\n",
        "\n",
        "MASK        6 4  S S NE\n",
        "EarPlugs    8 5  E N NW E N W W\n",
        "melatonin   6 1  s s e e n n w s\n",
        "Meditation  1 6  s nw w w se e se w w\n",
        "MOUTHGUARD  3 3  sw w n n n e s s ne\n",
        "BEDTIME     5 1  e e n e e e\n",
    ]

    for lines in [normal_lines, extra_spacing_lines, capitalization_lines]:
        game = StrandsGame(lines)

        assert game.theme() == '"Sleep tight"'
        assert game.board().num_rows() == 8
        assert game.board().num_cols() == 6
        assert game.answers() == sleep_tight_answers()


def test_load_game_sleep_tight_invalid() -> None:
    """
    Test that invalid versions of the sleep-tight game raise ValueError.
    """
    invalid_missing_board_letter = [
        '"Sleep tight"\n',
        "\n",
        "G U T I D\n",
        "H A D A T E\n",
        "T R M N O I\n",
        "U O T I M E\n",
        "B E D S G U\n",
        "M I N M P L\n",
        "E N O A K R\n",
        "L A T S E A\n",
        "\n",
        "mask 6 4 s s ne\n",
    ]

    invalid_wrong_answer_word = sleep_tight_lines().copy()
    invalid_wrong_answer_word[12] = "xxxx 6 4 s s ne\n"

    invalid_out_of_bounds_answer = sleep_tight_lines().copy()
    invalid_out_of_bounds_answer[12] = "mask 9 4 s s ne\n"

    invalid_bad_step = sleep_tight_lines().copy()
    invalid_bad_step[12] = "mask 6 4 s s banana\n"

    invalid_incomplete_answers = sleep_tight_lines()[:13]

    invalid_games = [
        invalid_missing_board_letter,
        invalid_wrong_answer_word,
        invalid_out_of_bounds_answer,
        invalid_bad_step,
        invalid_incomplete_answers,
    ]

    for lines in invalid_games:
        with pytest.raises(ValueError):
            StrandsGame(lines)


def test_play_game_sleep_tight_once() -> None:
    """
    Test playing all theme words in the listed answer order.
    """
    game = StrandsGame("boards/sleep-tight.txt")
    answers = sleep_tight_answers()

    assert not game.game_over()
    assert not game.found_strands()

    first_word, first_strand = answers[0]
    assert game.submit_strand(first_strand) == (first_word, True)
    assert game.found_strands() == [first_strand]
    assert not game.game_over()

    for word, strand in answers[1:]:
        assert game.submit_strand(strand) == (word, True)

    assert game.found_strands() == [strand for _, strand in answers]
    assert game.game_over()


def test_play_game_sleep_tight_twice() -> None:
    """
    Test playing all theme words in a different order.
    """
    game = StrandsGame("boards/sleep-tight.txt")
    answers = sleep_tight_answers()

    order = [5, 2, 0, 4, 1, 3]
    found = []

    for index in order:
        word, strand = answers[index]
        assert game.submit_strand(strand) == (word, True)
        found.append(strand)
        assert game.found_strands() == found

    assert game.game_over()


def test_play_game_sleep_tight_three_times() -> None:
    """
    Test theme words, already-found words, non-theme dictionary words,
    and too-short submissions.
    """
    game = StrandsGame("boards/sleep-tight.txt")
    answers = sleep_tight_answers()

    word, strand = answers[0]
    assert game.submit_strand(strand) == (word, True)
    assert game.submit_strand(strand) == "Already found"

    date = Strand(Pos(1, 2), [Step.E, Step.E, Step.E])
    assert game.submit_strand(date) == ("date", False)
    assert game.submit_strand(date) == "Already found"

    gut = Strand(Pos(0, 0), [Step.E, Step.E])
    assert game.submit_strand(gut) == "Too short"

    assert not game.game_over()


def test_play_game_sleep_tight_more() -> None:
    """
    Test hint behavior together with submitting theme words.
    """
    game = StrandsGame("boards/sleep-tight.txt", hint_threshold=1)
    answers = sleep_tight_answers()

    assert game.active_hint() is None
    assert game.use_hint() == "No hint yet"

    date = Strand(Pos(1, 2), [Step.E, Step.E, Step.E])
    assert game.submit_strand(date) == ("date", False)
    assert game.hint_meter() >= game.hint_threshold()

    assert game.use_hint() == (0, False)
    assert game.active_hint() == (0, False)

    assert game.use_hint() == (0, True)
    assert game.active_hint() == (0, True)

    assert game.use_hint() == "Use your current hint"

    word, strand = answers[0]
    assert game.submit_strand(strand) == (word, True)
    assert game.active_hint() is None

def test_play_game_G_hints_0() -> None:
    """
    Test using at least four successful hints for game G with threshold 0.
    """
    game = StrandsGame("boards/cs-142.txt", hint_threshold=0)

    for expected_index in range(4):
        assert game.use_hint() == (expected_index, False)
        word, strand = game.answers()[expected_index]
        assert game.submit_strand(strand) == (word, True)


def test_play_game_G_hints_1() -> None:
    """
    Test using at least four successful hints for game G with threshold 1.
    """
    game = StrandsGame("boards/cs-142.txt", hint_threshold=1)

    non_theme_words = [
    Strand(Pos(0, 0), [Step.S, Step.S, Step.E]),  # cone
    Strand(Pos(0, 1), [Step.SE, Step.E, Step.E]),  # sory
    Strand(Pos(0, 1), [Step.SE, Step.E, Step.NE]),  # sort
    Strand(Pos(0, 1), [Step.SE, Step.SE, Step.E]),  # sowt
]

    for expected_index, strand in enumerate(non_theme_words):
        result = game.submit_strand(strand)
        assert isinstance(result, tuple)
        assert result[1] is False
        assert game.hint_meter() >= game.hint_threshold()

        assert game.use_hint() == (expected_index, False)

        word, answer_strand = game.answers()[expected_index]
        assert game.submit_strand(answer_strand) == (word, True)

def test_play_game_H_hints_0() -> None:
    """
    Test using at least four successful hints for game H with threshold 0.
    """
    game = StrandsGame("boards/on-the-side.txt", hint_threshold=0)

    for expected_index in range(4):
        assert game.use_hint() == (expected_index, False)
        word, strand = game.answers()[expected_index]
        assert game.submit_strand(strand) == (word, True)


def test_play_game_H_hints_1() -> None:
    """
    Test using at least four successful hints for game H with threshold 1.
    """
    game = StrandsGame("boards/on-the-side.txt", hint_threshold=1)

    non_theme_words = [
    Strand(Pos(0, 0), [Step.S, Step.NE, Step.S, Step.SW]),  # nigre
    Strand(Pos(0, 0), [Step.S, Step.SE, Step.S, Step.NW]),  # nisse
    Strand(Pos(0, 1), [Step.S, Step.W, Step.N]),  # grin
    Strand(Pos(0, 1), [Step.S, Step.W, Step.SE]),  # gris
]

    for expected_index, strand in enumerate(non_theme_words):
        result = game.submit_strand(strand)
        assert isinstance(result, tuple)
        assert result[1] is False
        assert game.hint_meter() >= game.hint_threshold()

        assert game.use_hint() == (expected_index, False)

        word, answer_strand = game.answers()[expected_index]
        assert game.submit_strand(answer_strand) == (word, True)