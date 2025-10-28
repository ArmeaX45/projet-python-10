"""File: main.py"""

from src.game import Game
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

import pygame
import curses


if __name__ == "__main__":
    
    game = Game()

    halberdier = Halberdier(0,0)
    paladin = Paladin(11,11)
    arbalester = Arbalester(5,8)
    
    print(halberdier.instances)
    for soldat in halberdier.instances:
        game.add_to_soldat_group(soldat)
        game.add_on_grid(soldat)
        
    curses.wrapper(game.start_cmd)

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))

    # print("")
    # halberdier.attack(paladin)
    # print("")

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))



