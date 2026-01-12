# main.py
import time
import pygame
import math

from src.game import Game
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester
# from src.ia_braindead import GeneralBrainDead
from src.ai_daft import MajorDaftSimple

import pygame
import curses
import threading
    
# main.py
import pygame
import sys

# Import de ta nouvelle classe Map
from src.map import Map 

# Import des unités
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

from src.save_manager import save_game_state, load_game_state
from src.stats_generator import check_end_and_report

# ============================================================
#                      BLOC PRINCIPAL UNIQUE
# ============================================================

if __name__ == "__main__":
    # --- 1. INITIALISATION ---
    pygame.init()
    
    # On définit une taille d'écran (tu peux ajuster ou rendre dynamique)
    SCREEN_WIDTH = 2752
    SCREEN_HEIGHT = 1536
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Map Zoomable avec Soldat (Refactorisé)")
    
    # --- 2. CRÉATION DE LA MAP ---
    game_map = Map("./assets/image.png", screen.get_rect())
    game = Game(game_map, SCREEN_WIDTH//64, SCREEN_HEIGHT//64)

    # --- 3. GESTION DU CHARGEMENT (CLI) ---
    is_loaded = False
    if len(sys.argv) > 2 and sys.argv[1] == "load":
        filename = sys.argv[2]
        is_loaded = load_game_state(game, filename)

    # Si on n'a pas chargé de fichier, on crée les soldats par défaut
    if not is_loaded:
        game.create_soldat()
        print("[*] Nouvelle partie lancée.")
    else:
        print(f"[*] Partie chargée depuis {sys.argv[2]}")

    
    ia_daft = MajorDaftSimple(team_name=0)
    ia_brain = MajorDaftSimple(team_name=1)

    # --- 5. BOUCLE DE JEU ---
    running = True
    clock = pygame.time.Clock()

    # vie du sprite : 
    pygame.font.init()
    font = pygame.font.SysFont(None, 40) # Police taille 40
    soldat_selectionne = None
    #vie du sprite fin
    
    def run_curses(game):
        curses.wrapper(game.start_cmd)
    
    t = threading.Thread(target=run_curses, args=(game,))
    t.daemon = True   # permet au programme de s'arrêter même si le thread tourne
    t.start()

    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Petite touche pour quitter proprement aussi
                    running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # Clic Droit
                soldat_selectionne = None # On reset si on clique dans le vide
                for unit in game.all_soldats:
                    sx, sy = game_map.nouvelle_map(unit.rect.x, unit.rect.y)
                    w, h = unit.rect.width * game_map.current_scale, unit.rect.height * game_map.current_scale
                    
                    if pygame.Rect(sx, sy, w, h).collidepoint(event.pos):
                        soldat_selectionne = unit
                        break
            
            if event.type == pygame.KEYDOWN:
                # Sauvegarde Rapide (F11)
                if event.key == pygame.K_F11:
                    save_game_state(game, "quicksave.dat")

                # Chargement Rapide (F12)
                elif event.key == pygame.K_F12:
                    load_game_state(game, "quicksave.dat")

            # La classe map gère les actions possibles sur la map
            game_map.mouvement(event)

        # Affichage
        screen.fill((0, 0, 0))

        #  Dessiner la map
        game_map.draw(screen)

        #  Dessiner les soldats
        current_scale = game_map.current_scale # Récupérer le scale pour redimensionner les sprites

        for unit in game.all_soldats:
            
            # Position réelle 
            world_x = unit.rect.x
            world_y = unit.rect.y

            # Conversion vers Position Écran via la classe Map
            screen_x, screen_y = game_map.nouvelle_map(world_x, world_y)

            # Redimensionnement du sprite selon le zoom actuel
            soldat_w = int(unit.rect.width * current_scale)
            soldat_h = int(unit.rect.height * current_scale)
            
            #  vérifie que la taille est valide pour éviter les crashs si zoom  petit
            if soldat_w > 0 and soldat_h > 0:
                soldat_scaled_img = pygame.transform.scale(unit.image, (soldat_w, soldat_h))
                screen.blit(soldat_scaled_img, (screen_x, screen_y))
            
        # Si un soldat est sélectionné, on écrit son nom et ses PV 
        if soldat_selectionne:
            texte = f"{soldat_selectionne.name} : {soldat_selectionne.hp} PV"
            screen.blit(font.render(texte, True, (255, 255, 255)), (20, SCREEN_HEIGHT - 50))
        
        # --- 4. LOGIQUE DU JEU ---
        # --- décisions IA ---
        actions_A = ia_daft.update(game)
        actions_B = ia_brain.update(game)
        all_actions = actions_A + actions_B

        # --- exécution ---
        for action in all_actions:
            if action[0] == "move":
                _, unit, dx, dy = action
                unit.move(game, dx=dx, dy=dy)

            elif action[0] == "attack":
                _, unit, target = action
                if getattr(target, "is_alive", False):
                    unit.attack(target)
            if check_end_and_report(game):
                print("Fin du match enregistrée.")
        # 5) Affichage          
        pygame.display.flip()
        clock.tick(60) 

    pygame.quit()
    sys.exit()
