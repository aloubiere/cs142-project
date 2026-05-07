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
        if step == Step.N:
            result = Pos(self.r - 1, self.c)
        elif step == Step.S:
            result = Pos(self.r + 1, self.c)
        elif step == Step.E:
            result = Pos(self.r, self.c + 1)
        elif step == Step.W:
            result = Pos(self.r, self.c - 1)
        elif step == Step.NE:
            result = Pos(self.r - 1, self.c + 1)
        elif step == Step.NW:
            result = Pos(self.r - 1, self.c - 1)
        elif step == Step.SE:
            result = Pos(self.r + 1, self.c + 1)
        elif step == Step.SW:
            result = Pos(self.r + 1, self.c - 1)
        else:
            raise ValueError("Invalid step")
        return result


    def step_to(self, other: PosBase) -> Step:
        """
        Compute the difference in two positions,
        represented as a step from the current position to
        the other.

        Raises ValueError if the other position is more
        than one step away from self.
        """
        row_diff = other.r - self.r
        col_diff = other.c - self.c

        if row_diff == -1 and col_diff == 0:
            result = Step.N
        elif row_diff == 1 and col_diff == 0:
            result = Step.S
        elif row_diff == 0 and col_diff == 1:
            result = Step.E
        elif row_diff == 0 and col_diff == -1:
            result = Step.W
        elif row_diff == -1 and col_diff == -1:
            result = Step.NW
        elif row_diff == -1 and col_diff == 1:
            result = Step.NE
        elif row_diff == 1 and col_diff == -1:
            result = Step.SW
        elif row_diff == 1 and col_diff == 1:
            result = Step.SE
        else:
            raise ValueError("Positions are not adjacent")
        return result

    def is_adjacent_to(self, other: PosBase) -> bool:
        """
        Decide whether or not the two positions are
        neighbors (that is, connected by a single step).
        """
        row_diff = abs(other.r - self.r)
        col_diff = abs(other.c - self.c)

        return row_diff <= 1 and col_diff <= 1 and not (
            row_diff == 0 and col_diff == 0
        )
