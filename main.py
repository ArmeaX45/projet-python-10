# main.py
import time
import curses
import pygame
import sys
import threading

# Import de ta classe Map
from src.map import Map 
from src.game import Game
from src.ai_daft import MajorDaftSimple

# --- FONCTION UTILITAIRE POUR LA CONSOLE ---
def demander_compo(nom_equipe):
    """Demande à l'utilisateur la composition d'une équipe via la console."""
    print(f"\n--- CONFIGURATION {nom_equipe} ---")
    compo = {}
    
    try:
        h = input(f"Nombre de Hallebardiers (Halberdier) pour {nom_equipe} ? (defaut 5) : ")
        compo["Halberdier"] = int(h) if h.strip() else 5
        
        p = input(f"Nombre de Paladins (Paladin) pour {nom_equipe} ? (defaut 2) : ")
        compo["Paladin"] = int(p) if p.strip() else 2
        
        a = input(f"Nombre d'Arbalétriers (Arbalester) pour {nom_equipe} ? (defaut 2) : ")
        compo["Arbalester"] = int(a) if a.strip() else 2
        
    except ValueError:
        print("Entrée invalide détectée. Valeurs par défaut appliquées (5, 2, 2).")
        return {"Halberdier": 5, "Paladin": 2, "Arbalester": 2}
        
    return compo

if __name__ == "__main__":
    
    # --- 1. CONFIGURATION CONSOLE (AVANT PYGAME) ---
    print("=== BATAILLE MÉDIÉVALE : CONFIGURATION ===")
    config_team_0 = demander_compo("EQUIPE BLEUE (0)")
    config_team_1 = demander_compo("EQUIPE ROUGE (1)")
    
    full_config = {
        0: config_team_0,
        1: config_team_1
    }
    
    print("\nLancement de la simulation...")
    time.sleep(1)

    # --- 2. INITIALISATION PYGAME ---
    pygame.init()
    
    SCREEN_WIDTH = 2752
    SCREEN_HEIGHT = 1536
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE) 
    pygame.display.set_caption("Bataille Médiévale")
    
    # --- 3. CRÉATION DU JEU ---
    game_map = Map("./assets/image.png", screen.get_rect())
    game = Game(game_map, SCREEN_WIDTH//64, SCREEN_HEIGHT//64)

    # Création des soldats avec la config console
    game.create_soldat(full_config)
    
    # IA
    ia_daft = MajorDaftSimple(team_name=0)
    ia_brain = MajorDaftSimple(team_name=1)

    # --- 4. THREAD CONSOLE (Curses) ---
    def run_curses(game):
        try:
            curses.wrapper(game.start_cmd)
        except:
            pass
    
    t = threading.Thread(target=run_curses, args=(game,))
    t.daemon = True
    t.start()

    # --- 5. BOUCLE DE JEU ---
    running = True
    clock = pygame.time.Clock()

    pygame.font.init()
    font = pygame.font.SysFont(None, 40)
    font_victory = pygame.font.SysFont(None, 150, bold=True) # Police très grosse
    
    soldat_selectionne = None
    winner_text = ""

    while running:
        # -- Gestion Evénements --
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # Clic Droit
                soldat_selectionne = None
                for unit in game.all_soldats:
                    # Conversion coords monde -> écran
                    sx, sy = game_map.nouvelle_map(unit.rect.x, unit.rect.y)
                    w, h = unit.rect.width * game_map.current_scale, unit.rect.height * game_map.current_scale
                    
                    if pygame.Rect(sx, sy, w, h).collidepoint(event.pos):
                        soldat_selectionne = unit
                        break
            
            game_map.mouvement(event)

        # -- Logique (Arrêt si victoire) --
        if not winner_text:
            nb_alive_0 = len([u for u in game.all_soldats if u.team == 0])
            nb_alive_1 = len([u for u in game.all_soldats if u.team == 1])

            # Détection fin de partie
            if nb_alive_0 == 0 and nb_alive_1 == 0:
                winner_text = "MATCH NUL !"
            elif nb_alive_0 == 0:
                winner_text = "VICTOIRE ROUGE !"
            elif nb_alive_1 == 0:
                winner_text = "VICTOIRE BLEUE !"
            else:
                # Si personne n'a gagné, on update les IA
                actions_A = ia_daft.update(game)
                actions_B = ia_brain.update(game)
                all_actions = actions_A + actions_B

                for action in all_actions:
                    if action[0] == "move":
                        _, unit, dx, dy = action
                        unit.move(game, dx=dx, dy=dy)

                    elif action[0] == "attack":
                        _, unit, target = action
                        if getattr(target, "is_alive", False):
                            unit.attack(target)

        # -- Affichage --
        screen.fill((0, 0, 0))
        game_map.draw(screen)

        current_scale = game_map.current_scale

        for unit in game.all_soldats:
            world_x = unit.rect.x
            world_y = unit.rect.y
            screen_x, screen_y = game_map.nouvelle_map(world_x, world_y)

            soldat_w = int(unit.rect.width * current_scale)
            soldat_h = int(unit.rect.height * current_scale)
            
            if soldat_w > 0 and soldat_h > 0:
                soldat_scaled_img = pygame.transform.scale(unit.image, (soldat_w, soldat_h))
                screen.blit(soldat_scaled_img, (screen_x, screen_y))
            
        if soldat_selectionne and soldat_selectionne.is_alive:
            texte = f"{soldat_selectionne.name} : {soldat_selectionne.hp} PV"
            screen.blit(font.render(texte, True, (255, 255, 255)), (20, SCREEN_HEIGHT - 50))
        
        # -- Affichage VICTOIRE --
        if winner_text:
            # Texte Or (Gold)
            color_gold = (255, 215, 0)
            
            # Rendu du texte principal
            text_surf = font_victory.render(winner_text, True, color_gold)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
            # Rendu du contour (Ombre noire pour lisibilité)
            outline_surf = font_victory.render(winner_text, True, (0, 0, 0))
            outline_rect = outline_surf.get_rect(center=(SCREEN_WIDTH//2 + 5, SCREEN_HEIGHT//2 + 5))
            
            screen.blit(outline_surf, outline_rect) # Dessine l'ombre
            screen.blit(text_surf, text_rect)       # Dessine le texte
        
        pygame.display.flip()
        clock.tick(60) 

    pygame.quit()
    sys.exit()