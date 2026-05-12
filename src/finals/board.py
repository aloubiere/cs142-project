"""
Board Class Implementation
"""

from base import BoardBase, PosBase, StrandBase

class Board(BoardBase):
    """
    Boards for the Strands game, consisting of a
    rectangular grid of letters.
    """

    _letters: list[list[str]]

    def __init__(self, letters: list[list[str]]):
        """
        Constructor

        The two-dimensional matrix of strings (letters)
        is valid if (a) each row is non-empty and has
        the same length as other rows, and (b) each string
        is a single, lowercase, alphabetical character.

        Raises ValueError if the matrix is invalid.
        """
        if len(letters) == 0:
            raise ValueError("Board must have at least one row")

        num_cols = len(letters[0])

        if num_cols == 0:
            raise ValueError("Board rows must be non-empty")

        for row in letters:
            if len(row) != num_cols:
                raise ValueError("Board must be rectangular")

            for letter in row:
                if len(letter) != 1:
                    raise ValueError("Each board entry must be one character")
                if not letter.isalpha():
                    raise ValueError("Each board entry must be alphabetical")
                if not letter.islower():
                    raise ValueError("Each board entry must be lowercase")

        self._letters = letters

    def num_rows(self) -> int:
        """
        Return the number of rows on the board.
        """
        return len(self._letters)


    def num_cols(self) -> int:
        """
        Return the number of columns on the board.
        """
        return len(self._letters[0])


    def get_letter(self, pos: PosBase) -> str:
        """
        Return the letter at a given position on the board.

        Raises ValueError if the position is not within the
        bounds of the board.
        """
        if pos.r < 0 or pos.r >= self.num_rows():
            raise ValueError("Position row is out of bounds")

        if pos.c < 0 or pos.c >= self.num_cols():
            raise ValueError("Position column is out of bounds")

        return self._letters[pos.r][pos.c]

    def evaluate_strand(self, strand: StrandBase) -> str:
        """
        Evaluate a strand, returning the string of
        corresponding letters from the board.

        Raises ValueError if any of the strand's positions
        are not within the bounds of the board or if the
        strand is cyclic.
        """
        letters = []
        if strand.is_cyclic():
            raise ValueError("Strand may not be cyclic.")
        for pos in strand.positions():
            if pos.r < 0 or pos.r >= self.num_rows():
                raise ValueError("Strand position row is out of bounds")
            if pos.c < 0 or pos.c >= self.num_cols():
                raise ValueError("Strand position column is out of bounds")

            letters.append(self.get_letter(pos))

        return "".join(letters)
