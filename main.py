"""File: main.py"""

# from src.game import Game
from src.map import Map
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

import pygame
import curses
import time


if __name__ == "__main__":

    map = Map()

    halberdier = Halberdier(0,0)
    paladin = Paladin(10,1)
    arbalester = Arbalester(5,8)
    
    print(halberdier.instances)
    for soldat in halberdier.instances:
        map.add_to_soldat_group(soldat)
        map.add_on_grid(soldat)
    
    curses.wrapper(map.start_cmd)
    
    halberdier.move(map, dx=1)
    paladin.move(map, dy=1)
    arbalester.move(map, dy=-1)
    curses.wrapper(map.start_cmd)


    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))

    # print("")
    # halberdier.attack(paladin)
    # print("")

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))



