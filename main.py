"""File: main.py"""

from src.game import Game
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester
from src.ia_braindead import GeneralBrainDead

import pygame
import curses


if __name__ == "__main__":
    """
    game = Game()

    halberdier = Halberdier(0,0)
    paladin = Paladin(11,11)
    arbalester = Arbalester(5,8)
    
    print(halberdier.instances)
    for soldat in halberdier.instances:
        game.add_to_soldat_group(soldat)
        game.add_on_grid(soldat)
        
    curses.wrapper(game.start_cmd)
    """
    game = Game()

    h = Halberdier(0,0)
    h.team = "A"

    p = Paladin(4, 0)
    p.team = "B"

    game.add_to_soldat_group(h)
    game.add_to_soldat_group(p)

    ia = GeneralBrainDead(team_name="A")

    print("Position Halberdier :", h.rect.x, h.rect.y)
    print("Position Paladin :", p.rect.x, p.rect.y)

    actions = ia.update(game)

    print("\\nRésumé des actions retournées :")
    print(actions)

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))

    # print("")
    # halberdier.attack(paladin)
    # print("")

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))



