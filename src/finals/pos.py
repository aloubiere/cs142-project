"""
Pos Class Implementation
"""
# Vedat

from base import PosBase, Step

class Pos(PosBase):
    """
    Positions on a board, represented as pairs of 0-indexed
    row and column integers. Position (0, 0) corresponds to
    the top-left corner of a board, and row and column
    indices increase down and to the right, respectively.
    """

    # r: Row
    # c: Col

    def take_step(self, step: Step) -> PosBase:
        """
        Compute the position that results from starting at
        the current position and taking the specified step.
        """
        raise NotImplementedError


    def step_to(self, other: PosBase) -> Step:
        """
        Compute the difference in two positions,
        represented as a step from the current position to
        the other.

        Raises ValueError if the other position is more
        than one step away from self.
        """
        raise NotImplementedError


    def is_adjacent_to(self, other: PosBase) -> bool:
        """
        Decide whether or not the two positions are
        neighbors (that is, connected by a single step).
        """
        raise NotImplementedError
