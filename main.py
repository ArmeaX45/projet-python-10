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

# main.py
import sys
import pygame

# 🆕 AJOUT : Import des classes nécessaires
from src.halberdier import Halberdier

print(">>> Démarrage du script main.py")


if __name__ == "__main__":
    # --- 1. CONFIGURATION ---
    CHEMIN_IMAGE_MAP = "image.png" 
    ZOOM_STEP = 0.08
    MIN_ZOOM = 0.2
    MAX_ZOOM = 3.0
    
    dragging = False
    drag_last_pos = (0, 0)

    # --- 2. INITIALISATION ---
    pygame.init()
    print(">>> Pygame initialisé !")

    # --- 3. CHARGEMENT DE L'IMAGE ---
    try:
        original_map_image = pygame.image.load(CHEMIN_IMAGE_MAP)
    except pygame.error as e:
        print(f"ERREUR : Impossible de charger l'image : {CHEMIN_IMAGE_MAP}")
        sys.exit()

    # --- 4. CRÉATION DE LA FENÊTRE ---
    width, height = original_map_image.get_size()
    # On limite la taille de la fenêtre si l'image est trop grande (optionnel mais pratique)
    screen_width = min(1200, width)
    screen_height = min(900, height)
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    screen_rect = screen.get_rect() 
    pygame.display.set_caption("Map Zoomable avec Soldat")

    # ajout de soldats pour le test
    # Création de la map
    m = map()

    # --- 1 seul Halberdier (équipe A) ---
    team_A = []
    for i in range(10):
        h = Halberdier(i, 0, 0)
        team_A.append(h)
        m.add_to_soldat_group(h)
        m.add_on_grid(h)

    # --- 1 seul Paladin (équipe B) ---
    team_B = []
    for i in range(10):
        p = Halberdier(i, 9, 1)
        team_B.append(p)
        m.add_to_soldat_group(p)
        m.add_on_grid(p)

    # --- IA BrainDead pour l'équipe A ---
    ia = GeneralBrainDead(team_name=0)
    
    ia2 = GeneralBrainDead(team_name=1)

    tous_mes_soldats = team_A + team_B
    # On définit sa position "absolue" sur l'image de la carte (en pixels)
    # Par exemple : sur le chemin pavé vers le milieu
    soldat_world_x = 400 
    soldat_world_y = 300

    # --- 5. VARIABLES DE ZOOM ---
    original_map_image = original_map_image.convert()
    current_scale = 1.0
    current_map_image = original_map_image.copy()
    current_map_rect = current_map_image.get_rect(center=screen_rect.center)


    # IA teste une fois au lancement
    actions = ia.update(m)
    actions2 = ia2.update(m)
    for act in actions:
        if act[0] == "attack":
            _, unit, target = act
            unit.attack(target)
        elif act[0] == "move":
            _, unit, dx, dy = act
            unit.move(m, dx, dy)
    for act in actions2:
        if act[0] == "attack":
            _, unit, target = act
            unit.attack(target)
        elif act[0] == "move":
            _, unit, dx, dy = act
            unit.move(m, dx, dy)

    # --- 6. BOUCLE DE JEU ---
    IA_INTERVAL = 1.0
    last_ia_time = time.time()
    running = True
    font = pygame.font.SysFont("Arial", 18)
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- GESTION DU ZOOM (MOLETTE) ---
            if event.type == pygame.MOUSEWHEEL:
                old_scale = current_scale
                current_scale += event.y * ZOOM_STEP
                current_scale = max(MIN_ZOOM, min(current_scale, MAX_ZOOM))
                
                # Zoom centré sur la souris   
                new_width = int(original_map_image.get_width() * current_scale)
                new_height = int(original_map_image.get_height() * current_scale)
                
                # MAJ carte
                current_map_image = pygame.transform.scale(original_map_image, (new_width, new_height))
                
                # On récupère l'ancien centre 
                old_center = current_map_rect.center
                current_map_rect = current_map_image.get_rect(center=old_center)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    running = False

            # --- GESTION DU DRAG & DROP ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    drag_last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - drag_last_pos[0]
                    dy = event.pos[1] - drag_last_pos[1]
                    current_map_rect.x += dx
                    current_map_rect.y += dy
                    drag_last_pos = event.pos

        # ---  LOGIQUE DE JEU / IA ---
        current_time = time.time()
        if current_time - last_ia_time >= IA_INTERVAL:
            last_ia_time = current_time

            actions = ia.update(m)
            actions2 = ia2.update(m)

            for act in actions:
                if act[0] == "attack":
                    _, unit, target = act
                    if unit.is_alive and target.is_alive:
                        unit.attack(target)
                elif act[0] == "move":
                    _, unit, dx, dy = act
                    unit.move(m, dx, dy)
                for u in list(tous_mes_soldats):
                    if not u.is_alive:
                        tous_mes_soldats.remove(u)
            for act in actions2:
                if act[0] == "attack":
                    _, unit, target = act
                    if unit.is_alive and target.is_alive:
                        unit.attack(target)
                elif act[0] == "move":
                    _, unit, dx, dy = act
                    unit.move(m, dx, dy)
                for u in list(tous_mes_soldats):
                    if not u.is_alive:
                        tous_mes_soldats.remove(u)

            # Nettoyer les morts
            for u in list(m.all_soldats):
                if not u.is_alive:
                    print(f"{u.name} est mort !")
                    m.all_soldats.remove(u)

        #  AFFICHAGE 
        screen.fill((0,0,0))

        #  On dessine la carte
        screen.blit(current_map_image, current_map_rect)
        
        #  calcul et dessin du soldat
        
        for unit in tous_mes_soldats:
            # coordonnées dans le monde (les positions logiques du soldat)
            world_x = unit.rect.x
            world_y = unit.rect.y

            # Taille de l’image du soldat selon le zoom
            soldat_w = int(unit.rect.width * current_scale)
            soldat_h = int(unit.rect.height * current_scale)
            soldat_scaled_img = pygame.transform.scale(unit.image, (soldat_w, soldat_h))

            # Position sur l’écran (en fonction du zoom et du déplacement de la map)
            screen_soldat_x = current_map_rect.x + (world_x * current_scale)
            screen_soldat_y = current_map_rect.y + (world_y * current_scale)

            if not unit.is_alive:
                continue  # ne pas afficher le soldat mort

            # Dessine le soldat
            screen.blit(soldat_scaled_img, (screen_soldat_x, screen_soldat_y))

            # --- Afficher les PV au-dessus du soldat ---
            if unit.is_alive:
                hp_text = font.render(str(int(unit.hp)), True, (255, 255, 255))  # texte blanc
                text_x = screen_soldat_x + soldat_w // 2 - hp_text.get_width() // 2
                text_y = screen_soldat_y - 15
                screen.blit(hp_text, (text_x, text_y))

        pygame.display.flip()

    pygame.quit()