"""
Strands GUI Implementation
"""
# Amber

from sys import argv
from gui_files.gui import StrandGUI

if __name__ == "__main__":
    mode: str
    file: str
    match argv:
        case [_, "play", file]:
            StrandGUI(file, False).play()
        case [_, "show", file]:
            StrandGUI(file, True).play()
        case _:
            raise TypeError("Invalid arguments.")
