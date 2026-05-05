"""
StrandsGameFake Class Implementation
"""
# Palaash and Vedat

from base import StrandsGameBase, BoardBase, StrandBase, Step
from finals.pos import Pos
from finals.strand import Strand as StrandFake
from m1.boardfake import BoardFake

class StrandsGameFake(StrandsGameBase):
    """
    Class for Strands game logic.
    """

    _theme: str
    _board: BoardBase
    _answers: list[tuple[str, StrandBase]]
    _found_words: list[str]
    _found_strands: list[StrandBase]
    _hint_threshold_value: int
    _hint_meter_value: int
    _active_hint_value: None | tuple[int, bool]

    def __init__(
        self,
        game_file: str | list[str],
        hint_threshold: int = 3
        ):
        """
        Constructor

        Load the game specified in a given file, and set
        a particular threshold for giving hints. The game
        file can be specified either as a string filename,
        or as the list of lines that result from calling
        readlines() on the file.

        Raises ValueError if the game file is invalid.

        Valid game files include:

          1. a theme followed by a single blank line, then

          2. multiple lines defining the board followed
             by a single blank line, then

          3. multiple lines defining the answers,
             optionally followed by

          4. a blank line and then any number of remaining
             lines which have no semantic meaning.

        Valid game files require:

          - boards to be rectangular

          - boards where each string is a single,
            alphabetical character (either upper- or
            lower case; for example, both "a" and "A"
            denote the same letter, which is stored
            as "a" in the board object)

          - each line for an answer of the form
            "WORD R C STEP1 STEP2 ..." where
              * WORD has at least three letters,
              * the position (R, C) is within bounds
                of the board,
              * the positions implied by the steps are
                all within bounds of the board, and
              * the letters implied by the strand
                spell the WORD (modulo capitalization)
              * the WORDs and STEPs may be spelled with
                either lower- or uppercase letters, but
                regardless the WORDs are stored in the
                game object with only lowercase letters.

           - that answers fill the board

        Game files are allowed to use multiple space
        characters to separate tokens on a line. Also,
        leading and trailing whitespace will be ignored.
        """

        self._hint_threshold = hint_threshold
        self._hint_meter = 0
        self._active_hint = None
        self._found_indices = []
        self._found_strands = []

        if isinstance(game_file, str):
            with open(game_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = game_file

        sections: list[list[str]] = []
        current_section: list[str] = []

        for line in lines:
            stripped = line.strip()

            if stripped == "":
                if current_section:
                    sections.append(current_section)
                    current_section = []
            else:
                current_section.append(stripped)

        if current_section:
            sections.append(current_section)

        if len(sections) < 3:
            raise ValueError("Game file must include theme, board, and answers")

        theme_line = sections[0][0]
        self._theme = theme_line

        letters: list[list[str]] = []

        for board_line in sections[1]:
            row = []

            for token in board_line.split():
                row.append(token.lower())

            letters.append(row)

        self._board = BoardFake(letters)

        self._answers = []

        for answer_line in sections[2]:
            tokens = answer_line.split()

            if len(tokens) < 3:
                raise ValueError("Answer line must include word, row, and column")

            word = tokens[0].lower()
            row = int(tokens[1]) - 1
            col = int(tokens[2]) - 1

            steps: list[Step] = []

            for token in tokens[3:]:
                steps.append(Step(token.lower()))

            strand = StrandFake(Pos(row, col), steps)

            if self._board.evaluate_strand(strand) != word:
                raise ValueError("Answer strand does not spell answer word")

            self._answers.append((word, strand))

    def theme(self) -> str:
        """
        Return the theme for the game.
        """
        return self._theme

    def board(self) -> BoardBase:
        """
        Return the board for the game.
        """
        return self._board

    def answers(self) -> list[tuple[str, StrandBase]]:
        """
        Return the answers for the game. Each answer
        is a pair comprising a theme word and the
        corresponding strand on the board. Words are
        stored using lowercase letters, even if the
        game file used uppercase letters.
        """
        return self._answers

    def found_strands(self) -> list[StrandBase]:
        """
        Return the theme words that have been found so far,
        represented as strands. The order of strands in the
        output matches the order in which they were found.

        Note two strands may overlap, meaning they involve
        different sequences of steps yet identify the same
        absolute positions on the board. This method
        returns the strands that have been submitted
        through the user interface (i.e. submit_strand)
        and thus may deviate from the strands stored in
        answers.
        """
        return self._found_strands

    def game_over(self) -> bool:
        """
        Decide whether or not the game is over, which means
        checking whether or not all theme words have been
        found.
        """
        return len(self._found_indices) == len(self._answers)

    def hint_threshold(self) -> int:
        """
        Return the hint threshold for the game.
        """
        return self._hint_threshold

    def hint_meter(self) -> int:
        """
        Return the current hint meter for the game.
        If it is greater than or equal to the hint
        threshold, then the user can request a hint.
        """
        return self._hint_meter

    def active_hint(self) -> None | tuple[int, bool]:
        """
        Return the active hint, if any.

        Returns None:
            if there is no active hint.

        Returns (i, False):
            if the active hint corresponds to the ith
            answer in the list of answers, but the start
            and end positions _should not_ be shown to the
            user.

        Returns (i, True):
            if the active hint corresponds to the ith
            answer in the list of answers, and the start
            and end positions _should_ be shown to the
            user.
        """
        return self._active_hint

    def submit_strand(
        self,
        strand: StrandBase
        ) -> tuple[str, bool] | str:
        """
        Play a selected strand.

        Returns (word, True):
            if the strand corresponds to a theme word which
            has not already been found.

        Returns (word, False):
            if the strand does not correspond to a theme
            word but does correspond to a valid dictionary
            word that has not already been found.

        Returns "Already found":
            if the strand corresponds to a theme word or
            dictionary word that has already been found.

        Returns "Too short":
            if the strand corresponds to fewer than four
            letters (unless it is a three-letter theme
            word, in which case the result is
            (word, True)).

        Returns "Not in word list":
            if the strand corresponds to a string that
            is not a valid dictionary word.
        """
        for i, answer in enumerate(self._answers):
            word, answer_strand = answer

            if strand.start == answer_strand.start:
                if i in self._found_indices:
                    return "Already found"

                self._found_indices.append(i)
                self._found_strands.append(answer_strand)

                if self._active_hint is not None:
                    hint_index, _ = self._active_hint

                    if hint_index == i:
                        self._active_hint = None

                return (word, True)

        return "Not a theme word"

    def use_hint(self) -> tuple[int, bool] | str:
        """
        Play a hint.

        Returns (i, b):
            if successfully updated the active hint. The
            new hint corresponds to the ith answer in the
            list of all answers, which is the first answer
            that has not already been found. The boolean b
            describes whether there was already an active
            hint before this call to use_hint (and thus
            whether or not the first and last letters of
            the hint word should be highlighted).

        Returns "No hint yet":
            if the current hint meter does not yet warrant
            a hint.

        Returns "Use your current hint":
            if there is already an active hint where the
            first and last letters are being displayed.
        """
        if self._active_hint is None:
            for i, _ in enumerate(self._answers):
                if i not in self._found_indices:
                    self._active_hint = (i, False)
                    return (i, False)

            return "No hint yet"

        hint_index, show_start_end = self._active_hint

        if not show_start_end:
            self._active_hint = (hint_index, True)
            return (hint_index, True)

        return "Use your current hint"
