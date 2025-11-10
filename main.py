# main.py
import time
import curses
import pygame

from src.map import map
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester
from src.ia_braindead import GeneralBrainDead

import pygame
import curses 

""" Youssef
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
"""


if __name__ == "__main__":
    """
    game = Game()
    
    pygame.init()

    # 1. Créer l'objet carte (charge l'image)
    game_map = map("mamap.png")

    # 2. Définir la taille de l'écran (basée sur la taille de l'image)
    if game_map.image:
        width, height = game_map.image.get_size()
    else:
        width, height = 1000, 800 # Taille par défaut si l'image n'est pas chargée

    # 3. Créer la fenêtre (l'objet 'screen')
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Ma Fenêtre Pygame")


    running = True
    while running:
        # Gère les actions de l'utilisateur (événements)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Si l'utilisateur clique sur la croix
                running = False           # On sort de la boucle
                

        game_map.draw_map(screen)  # Demande à la carte de se dessiner sur l'écran 
        
    curses.wrapper(game.start_cmd)
    """
    m = map()

    h = Halberdier(1,0)
    h.team = "A"

    p = Paladin(2, 3)
    p.team = "B"

    m.add_to_soldat_group(h)
    m.add_to_soldat_group(p)
    m.add_on_grid(h)
    m.add_on_grid(p)

    ia = GeneralBrainDead(team_name="A")
    ia2 = GeneralBrainDead(team_name="B")

    

    m.print_grid()
    for tour in range(10):
        print(f"===== TOUR {tour+1} =====")
        actions = ia.update(m)
        actions2 = ia2.update(m)
        for act in actions:
            if act[0] == "attack":
                _, unit, target = act
                if unit.is_alive and target.is_alive:
                    unit.attack(target)
                    print(f"{target.name} a {target.hp} HP.")
            elif act[0] == "move":
                _, unit, dx, dy = act
                unit.move(m, dx, dy)
        for act in actions2:
            if act[0] == "attack":
                _, unit, target = act
                if unit.is_alive and target.is_alive:
                    unit.attack(target)
                    print(f"{target.name} a {target.hp} HP.")
            elif act[0] == "move":
                _, unit, dx, dy = act
                unit.move(m, dx, dy)
        print(actions)
        print(actions2)
        m.print_grid()
        for s in list(m.all_soldats):
            if not s.is_alive:
                print(f"{s.name} est mort !")
                m.all_soldats.remove(s)




"""
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
"""

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))

    # print("")
    # halberdier.attack(paladin)
    # print("")

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))

""" 
    for s in [h0, p1, a1]:
        game.add_to_soldat_group(s)
        game.add_on_grid(s)



game = Game()
    game.general_p0 = MajorDaft()        # Joueur 0 : DAFT
    game.general_p1 = CaptainBraindead() # Joueur 1 : BRAINDEAD

    # --- Place des unités (pense au owner) ---
    # Camp 0 (DAFT)
    h0 = Halberdier(0, 0);  h0.owner = 0
    # Camp 1 (BRAINDEAD)
    p1 = Paladin(11, 11);   p1.owner = 1
    a1 = Arbalester(5, 8);  a1.owner = 1
"""