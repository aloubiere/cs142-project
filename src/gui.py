"""
Strands GUI Implementation
"""
# Amber

from sys import argv
from gui_files.gui import StrandGUI

if __name__ == "__main__":
    match argv:
        case [_, "play", str() as file]:
            StrandGUI(file, False).play()
        case [_, "show", str() as file]:
            StrandGUI(file, True).play()
        case _:
            raise TypeError("Invalid arguments.")
