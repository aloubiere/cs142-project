"""
Strands GUI Implementation
"""
# Amber

from pathlib import Path
from glob import glob
from random import choice
from click import command, option
from gui_files.gui import StrandGUI


@command("src/gui.py")
@option("--show", "mode", is_flag = True)
@option("--game", "-g", "game")
@option("--hint", "-h", "hint_threshold", type = int)
def play(
    mode: bool = False,
    game: str | None = None,
    hint_threshold: int | None = None
    ) -> None:
    """ play the game Strands """
    root = Path(__file__).resolve().parents[1]
    if game is None:
        file = choice(glob(str(root / "boards/*.txt")))
    else:
        file = str(root / f"boards/{game}.txt")
    StrandGUI(file, mode, hint_threshold).play()

if __name__ == "__main__":
    play()
