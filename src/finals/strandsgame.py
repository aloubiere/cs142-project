"""
StrandsGame Class Implementation
"""
# Palaash and Vedat and Amber

from base import (
    Step, PosBase, StrandsGameBase, BoardBase, StrandBase
    )
from finals.pos import Pos
from finals.strand import Strand
from finals.board import Board


class StrandsGame(StrandsGameBase):
    """
    Class for Strands game logic.
    """

    # Class Attribute
    _dictionary: set[str] = set()

    # Instance Attribute
    _theme: str
    _board: BoardBase
    _answers: list[tuple[str, StrandBase]]
    _found_strands: list[StrandBase]
    _found_words: set[str]
    _hint_threshold: int
    _hint_meter: int
    _active_hint: None | tuple[int, bool]


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
        # type check inputted arguments
        if not isinstance(hint_threshold, int):
            raise TypeError(
                "The argument `hint_threshold` must be an \
                integer."
                )
        if isinstance(game_file, str):
            with open(game_file, "r", encoding = "utf-8") as file:
                lines = file.readlines()
        elif (
            isinstance(game_file, list)
            and all(
                isinstance(line, str) for line in game_file
                )
            ):
            lines = game_file
        else:
            raise TypeError(
                "The argument `game_file` must be a \
                string file name or a list of strings \
                that results from calling readlines() on \
                a game file."
                )

        # process lines
        blanks = 0
        letters: list[list[str]] = []
        answers: list[list[str]] = []
        for line in lines:
            stripped = line.strip()
            if stripped == "":
                blanks += 1
                continue
            if blanks == 0:
                self._theme = stripped
            elif blanks == 1:
                letters.append(stripped.lower().split())
            elif blanks == 2:
                answers.append(stripped.lower().split())
            else:
                break

        # initialize attributes
        self._board = Board(letters)
        self._process_answers(answers)
        self._hint_threshold = hint_threshold
        self._hint_meter = 0
        self._found_strands = []
        self._found_words = set()
        self._active_hint = None


    def _process_answers(
        self,
        answers: list[list[str]]
        ) -> None:
        """
        Process the list of answer lines obtained from
        reading a game file.

        Raises ValueError if the answers are invalid, as
        described by the constructor.
        """
        unused: list[PosBase] = [
            Pos(i, j)
            for i in range(self._board.num_rows())
            for j in range(self._board.num_cols())
            ]
        self._answers = []
        for answer in answers:
            try:
                word = answer[0]
                strand = Strand(
                    Pos(
                        int(answer[1]) - 1,
                        int(answer[2]) - 1
                        ),
                    [Step(step) for step in answer[3:]]
                    )
            except (IndexError, ValueError) as exc:
                raise ValueError(
                    "Unable to read answers"
                    ) from exc
            if self._board.evaluate_strand(strand) != word:
                raise ValueError(
                    "Answer strand does not spell the \
                    answer word"
                    )
            if len(word) < 3:
                raise ValueError(
                    "Answer word must be at least 3 \
                    letters long."
                    )
            for pos in strand.positions():
                if pos not in unused:
                    raise ValueError(
                        "Answer strands overlap"
                        )
                unused.remove(pos)
            self._answers.append((word, strand))
        if unused:
            raise ValueError(
                "Answer strands do not fill the board."
                )


    @classmethod
    def load_dictionary(cls, filename: str) -> None:
        """
        load valid words from the dictionary file given
        """
        if not isinstance(filename, str):
            raise TypeError(
                "The argument `filename` must be a string."
                )
        with open(filename, 'r', encoding = 'utf-8') as file:
            cls._dictionary = set()
            for line in file:
                word = line.strip().lower()
                if word.isalpha() and len(word) >= 4:
                    cls._dictionary.add(word)


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
        return len(self.found_strands()) == len(self.answers())


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
        if not isinstance(strand, StrandBase):
            raise TypeError(
                "The argument `strand` must be a \
                StrandBase object."
                )
        word = self._board.evaluate_strand(strand)
        if word in self._found_words:
            return "Already found"
        answer_strand = next(
                (s for w, s in self.answers() if w == word),
                None
                )
        if answer_strand is not None:
            self._found_words.add(word)
            # update active_hint
            if self._active_hint is not None:
                i = self._active_hint[0]
                if word == self.answers()[i][0]:
                    self._active_hint = None
            # update found_strands
            positions = answer_strand.positions()
            for pos in strand.positions():
                if pos not in positions:
                    strand = answer_strand
                    break
            self._found_strands.append(strand)
            return (word, True)
        if len(word) < 4:
            return "Too short"
        if word in self._dictionary:
            self._found_words.add(word)
            self._hint_meter += 1
            return (word, False)
        else:
            return "Not in word list"


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
        assert not self.game_over(), \
            "Calling use_hint() after the game is over."
        match self.active_hint():
            case (int(), True):
                return "Use your current hint"
            case _ if self.hint_meter() < self.hint_threshold():
                return "No hint yet"
            case (int() as i, False):
                hint = (i, True)
            case None:
                i = next(
                    i for i, (w, _)
                    in enumerate(self.answers())
                    if w not in self._found_words
                    )
                hint = (i, False)
        self._hint_meter -= self.hint_threshold()
        self._active_hint = hint
        return hint


StrandsGame.load_dictionary("assets/web2.txt")
