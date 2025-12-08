# main.py
import time
import curses
import pygame

from src.game import Game
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester
from src.ia_braindead import GeneralBrainDead

import pygame
import curses
import threading

if __name__ == "__main__":

    game = Game()

    halberdier = Halberdier(0,0)
    paladin = Paladin(1,0)
    arbalester = Arbalester(5,8)
    
    all_soldat = [ halberdier, paladin, arbalester ]
    
    for soldat in all_soldat:
        game.add_to_soldat_group(soldat)
        game.add_on_grid(soldat)
    
    def run_curses(game):
        curses.wrapper(game.start_cmd)
    
    t = threading.Thread(target=run_curses, args=(game,))
    t.daemon = True   # permet au programme de s'arrêter même si le thread tourne
    t.start()

    time.sleep(2)
    halberdier.move(game, dx=1)
    arbalester.move(game, dy=-1)
    time.sleep(2)
    paladin.move(game, dy=1)
    arbalester.is_alive = False
    time.sleep(2)