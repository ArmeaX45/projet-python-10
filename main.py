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
from src.ia_braindead import GeneralBrainDead
from src.ColonelSMART import ColonelSMART


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
    
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE) 
    pygame.display.set_caption("Bataille Médiévale")
    
    # --- 3. CRÉATION DU JEU ---
    game_map = Map("./assets/image.png", screen.get_rect())
    # Grille plus grande pour les sprites plus petits (2x plus de cases)
    game = Game(game_map, SCREEN_WIDTH//32, SCREEN_HEIGHT//32)
    
    # --- MINIMAP INDÉPENDANTE ---
    # Charger l'image de la map et créer une version miniature
    minimap_original = pygame.image.load("./assets/image.png").convert()
    MINIMAP_W = 200
    MINIMAP_H = 113
    # Calculer les dimensions en conservant le ratio
    orig_ratio = minimap_original.get_width() / minimap_original.get_height()
    if orig_ratio > MINIMAP_W / MINIMAP_H:
        final_mm_w = MINIMAP_W
        final_mm_h = int(MINIMAP_W / orig_ratio)
    else:
        final_mm_h = MINIMAP_H
        final_mm_w = int(MINIMAP_H * orig_ratio)
    
    minimap_img = pygame.transform.smoothscale(minimap_original, (final_mm_w, final_mm_h))
    minimap_scale = final_mm_w / minimap_original.get_width()
    print(f"[MINIMAP] Créée: {final_mm_w}x{final_mm_h}, scale={minimap_scale:.4f}")

    # IA (créées AVANT les soldats pour définir les formations)
    ia_daft = MajorDaftSimple(team_name=1)
    ia_brain = ColonelSMART(team_name=0)
    
    # Création des soldats avec les formations définies par les IA
    game.create_soldat(full_config, ai_team0=ia_brain, ai_team1=ia_daft)

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
    paused = False  # État de pause
    
    # --- CACHE D'IMAGES POUR OPTIMISATION ---
    # Stocke les images mises à l'échelle pour chaque taille
    image_cache = {}
    last_scale = -1

    while running:
        # -- Gestion Evénements --
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused  # Toggle pause
            
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

        # -- Logique (Arrêt si victoire ou pause) --
        if not winner_text and not paused:
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
        
        # Vider le cache si le zoom a changé
        if current_scale != last_scale:
            image_cache.clear()
            last_scale = current_scale

        # Dessiner tous les soldats avec cache d'images
        for unit in game.all_soldats:
            # Mettre à jour l'animation
            unit.update_animation()
            
            world_x = unit.rect.x
            world_y = unit.rect.y
            screen_x, screen_y = game_map.nouvelle_map(world_x, world_y)

            soldat_w = int(unit.rect.width * current_scale)
            soldat_h = int(unit.rect.height * current_scale)
            
            if soldat_w > 0 and soldat_h > 0:
                # Utiliser le cache d'images
                cache_key = (id(unit.image), soldat_w, soldat_h)
                if cache_key not in image_cache:
                    image_cache[cache_key] = pygame.transform.scale(unit.image, (soldat_w, soldat_h))
                
                screen.blit(image_cache[cache_key], (screen_x, screen_y))
                
                # --- BARRE DE VIE ---
                hp_ratio = unit.hp / unit.max_hp
                bar_width = int(soldat_w * 0.7)
                bar_height = max(2, int(3 * current_scale))
                bar_x = screen_x + (soldat_w - bar_width) // 2
                bar_y = screen_y - bar_height - 1
   
                # Fond de la barre (noir)
                pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                
                # Couleur de la barre (vert -> rouge selon HP)
                green = max(0, min(255, int(255 * hp_ratio)))
                red = max(0, min(255, int(255 * (1 - hp_ratio))))
                bar_color = (red, green, 0)
                
                # Barre de vie
                hp_width = int(bar_width * hp_ratio)
                if hp_width > 0:
                    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, hp_width, bar_height))
                
                # Contour blanc
                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # --- MINIMAP DESSINÉE EN DERNIER (au-dessus de tout) ---
        actual_screen_w = screen.get_width()
        actual_screen_h = screen.get_height()
        
        # Position en haut à droite
        mm_margin = 15
        mm_x = actual_screen_w - final_mm_w - mm_margin
        mm_y = mm_margin
        
        # Fond noir opaque
        pygame.draw.rect(screen, (30, 30, 30), (mm_x - 5, mm_y - 5, final_mm_w + 10, final_mm_h + 10))
        # Bordure dorée épaisse
        pygame.draw.rect(screen, (180, 140, 60), (mm_x - 5, mm_y - 5, final_mm_w + 10, final_mm_h + 10), 4)
        
        # Image minimap (variable créée en haut du fichier)
        screen.blit(minimap_img, (mm_x, mm_y))
        
        # Cadre rouge viewport
        view_x = -game_map.rect.x / game_map.current_scale * minimap_scale
        view_y = -game_map.rect.y / game_map.current_scale * minimap_scale
        view_w = actual_screen_w / game_map.current_scale * minimap_scale
        view_h = actual_screen_h / game_map.current_scale * minimap_scale
        
        viewport = pygame.Rect(mm_x + view_x, mm_y + view_y, view_w, view_h)
        viewport = viewport.clip(pygame.Rect(mm_x, mm_y, final_mm_w, final_mm_h))
        if viewport.width > 0 and viewport.height > 0:
            pygame.draw.rect(screen, (255, 50, 50), viewport, 2)
        
        # --- SOLDATS SUR LA MINIMAP ---
        for unit in game.all_soldats:
            # Convertir position monde -> minimap
            soldier_mm_x = mm_x + int(unit.rect.centerx * minimap_scale)
            soldier_mm_y = mm_y + int(unit.rect.centery * minimap_scale)
            
            # Couleur selon l'équipe
            if unit.team == 0:
                dot_color = (50, 100, 255)  # Bleu
            else:
                dot_color = (255, 50, 50)   # Rouge
            
            # Dessiner le point (rayon 2-3 pixels)
            pygame.draw.circle(screen, dot_color, (soldier_mm_x, soldier_mm_y), 2)
            
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
        
        # -- Affichage PAUSE style médiéval --
        if paused and not winner_text:
            # Compter les soldats
            nb_bleus = len([u for u in game.all_soldats if u.team == 0])
            nb_rouges = len([u for u in game.all_soldats if u.team == 1])
            
            # Fond semi-transparent
            pause_overlay = pygame.Surface((600, 300), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 180))
            screen.blit(pause_overlay, (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150))
            
            # Bordure dorée
            pygame.draw.rect(screen, (212, 175, 55), (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300), 4)
            
            # Titre "HALTE !" style médiéval
            color_gold = (212, 175, 55)
            pause_title = font_victory.render("~ Pause ~", True, color_gold)
            title_rect = pause_title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            screen.blit(pause_title, title_rect)
            
            # Compteurs d'armées
            font_pause = pygame.font.SysFont(None, 50)
            
            # Équipe bleue
            bleu_text = font_pause.render(f"Armée Bleue: {nb_bleus} soldats", True, (100, 150, 255))
            bleu_rect = bleu_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            screen.blit(bleu_text, bleu_rect)
            
            # Équipe rouge
            rouge_text = font_pause.render(f"Armée Rouge: {nb_rouges} soldats", True, (255, 100, 100))
            rouge_rect = rouge_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            screen.blit(rouge_text, rouge_rect)
            
            # Instructions
            font_small = pygame.font.SysFont(None, 30)
            hint_text = font_small.render("Appuyez sur ESPACE pour reprendre", True, (180, 180, 180))
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
            screen.blit(hint_text, hint_rect)
        
        pygame.display.flip()
        clock.tick(60) 

    pygame.quit()
    sys.exit()