"""
StrandFake Class Implementation
"""
# Amber

from base import StrandBase, PosBase

class StrandFake(StrandBase):
    """
    Strands, represented as a start position
    followed by a sequence of steps.
    """

    # start: PosBase
    # steps: list[Step]

    def positions(self) -> list[PosBase]:
        """
        Compute the absolute positions represented by the
        strand. These positions are independent of any
        particular board size. That is, the resulting
        positions assume a board of infinite size in all
        directions.
        """
        raise NotImplementedError


    def is_cyclic(self) -> bool:
        """
        Decide whether or not the strand is cyclic. That
        is, check whether or not any position appears
        multiple times in the strand.
        """
        raise NotImplementedError
