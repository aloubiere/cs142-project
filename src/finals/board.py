"""
Board Class Implementation
"""
# pylint: disable = duplicate-code

from base import BoardBase, PosBase, StrandBase

class Board(BoardBase):
    """
    Boards for the Strands game, consisting of a
    rectangular grid of letters.
    """


    def __init__(self, letters: list[list[str]]):
        """
        Constructor

        The two-dimensional matrix of strings (letters)
        is valid if (a) each row is non-empty and has
        the same length as other rows, and (b) each string
        is a single, lowercase, alphabetical character.

        Raises ValueError if the matrix is invalid.
        """
        raise NotImplementedError


    def num_rows(self) -> int:
        """
        Return the number of rows on the board.
        """
        raise NotImplementedError


    def num_cols(self) -> int:
        """
        Return the number of columns on the board.
        """
        raise NotImplementedError


    def get_letter(self, pos: PosBase) -> str:
        """
        Return the letter at a given position on the board.

        Raises ValueError if the position is not within the
        bounds of the board.
        """
        raise NotImplementedError


    def evaluate_strand(self, strand: StrandBase) -> str:
        """
        Evaluate a strand, returning the string of
        corresponding letters from the board.

        Raises ValueError if any of the strand's positions
        are not within the bounds of the board.
        """
        raise NotImplementedError
