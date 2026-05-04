"""
StrandFake Class Implementation
"""
# Amber

from base import StrandBase, PosBase

class Strand(StrandBase):
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
        positions = [self.start]
        for step in self.steps:
            positions.append(positions[-1].take_step(step))
        return positions


    def is_cyclic(self) -> bool:
        """
        Decide whether or not the strand is cyclic. That
        is, check whether or not any position appears
        multiple times in the strand.
        """
        positions = self.positions()
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                if pos1 == pos2:
                    return True
        return False
