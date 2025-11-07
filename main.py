"""File: main.py"""

from src.map import map
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester
from src.ia_braindead import GeneralBrainDead

import pygame
import curses 


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

    h = Halberdier(0,0)
    h.team = "A"

    p = Paladin(0, 4)
    p.team = "B"

    m.add_to_soldat_group(h)
    m.add_to_soldat_group(p)
    m.add_on_grid(h)
    m.add_on_grid(p)

    ia = GeneralBrainDead(team_name="A")

    print("Position Halberdier :", h.rect.x, h.rect.y)
    print("Position Paladin :", p.rect.x, p.rect.y)

    actions = ia.update(m)

    m.print_grid()

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


