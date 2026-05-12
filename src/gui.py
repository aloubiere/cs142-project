"""
Strands GUI Implementation
"""
# Amber

from sys import argv
from glob import glob
from random import choice
from gui_files.gui import StrandGUI

if __name__ == "__main__":
    match argv:
        case [_, "play", str() as file]:
            StrandGUI(file, False).play()
        case [_, "show", str() as file]:
            StrandGUI(file, True).play()
        case [_, "play"]:
            file = choice(glob("boards/*.txt"))
            StrandGUI(file, False).play()
        case [_, "show"]:
            file = choice(glob("boards/*.txt"))
            StrandGUI(file, True).play()
        case [_]:
            StrandGUI("boards/cs-142.txt", False).play()
        case _:
            raise TypeError("Invalid arguments.")
