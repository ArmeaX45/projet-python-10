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
    tous_mes_soldats = [{"soldat" : Halberdier(x, y)} for x in range(0, 10) for y in range(0,10)] + [{"soldat" : Paladin(x, y)} for x in range(0, 10) for y in range(10,20)]
    
    # On définit sa position "absolue" sur l'image de la carte (en pixels)
    # Par exemple : sur le chemin pavé vers le milieu
    soldat_world_x = 400 
    soldat_world_y = 300

    # --- 5. VARIABLES DE ZOOM ---
    original_map_image = original_map_image.convert()
    current_scale = 1.0
    current_map_image = original_map_image.copy()
    current_map_rect = current_map_image.get_rect(center=screen_rect.center)

    # --- 6. BOUCLE DE JEU ---
    running = True
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

        #  AFFICHAGE 
        screen.fill((0,0,0))

        #  On dessine la carte
        screen.blit(current_map_image, current_map_rect)
        
        #  calcul et dessin du soldat
        
        for s in tous_mes_soldats:
            unit = s["soldat"]
            world_x = s["soldat"].rect.x
            world_y = s["soldat"].rect.y

            # Redimensionner selon le zoom
            soldat_w = int(unit.rect.width * current_scale)
            soldat_h = int(unit.rect.height * current_scale)
            soldat_scaled_img = pygame.transform.scale(unit.image, (soldat_w, soldat_h))
        
            #  Calculer la position écran
            screen_soldat_x = current_map_rect.x + (world_x * current_scale)
            screen_soldat_y = current_map_rect.y + (world_y * current_scale)
            
            #  Dessiner
            screen.blit(soldat_scaled_img, (screen_soldat_x, screen_soldat_y))

        pygame.display.flip()

    pygame.quit()