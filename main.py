# main.py
import time
import curses
import pygame

from src.game import Game
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester
from src.ai_daft import MajorDaft
from src.ai_braindead import CaptainBraindead

def run_curses(stdscr, game: Game, ticks: int = 200, dt: float = 0.08):
    curses.curs_set(0)
    stdscr.nodelay(True)

    for _ in range(ticks):
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q')):
            break

        game.logic_tick()

        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        title = "DAFT (J0) vs BRAINDEAD (J1) — q pour quitter"
        stdscr.addstr(0, 0, title[:max_x - 1])  # titre tronqué
        game.show_grid(stdscr)
        stdscr.refresh()
        curses.napms(int(dt * 1000))  # évite flicker, portable


if __name__ == "__main__":
    pygame.init()

    game = Game()
    game.general_p0 = MajorDaft()        # Joueur 0 : DAFT
    game.general_p1 = CaptainBraindead() # Joueur 1 : BRAINDEAD

    # --- Place des unités (pense au owner) ---
    # Camp 0 (DAFT)
    h0 = Halberdier(0, 0);  h0.owner = 0
    # Camp 1 (BRAINDEAD)
    p1 = Paladin(11, 11);   p1.owner = 1
    a1 = Arbalester(5, 8);  a1.owner = 1

    for s in [h0, p1, a1]:
        game.add_to_soldat_group(s)
        game.add_on_grid(s)

    curses.wrapper(lambda stdscr: run_curses(stdscr, game))
    pygame.quit()

