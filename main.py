"""File: main.py"""

from src.map import map
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

import pygame
import curses 


if __name__ == "__main__":
        # --- 1. CONFIGURATION ---
    CHEMIN_IMAGE_MAP = "D:\projet-python-10\image.png"  # Mets le bon chemin ici
    ZOOM_STEP = 0.08  # Vitesse du zoom (10% par coup de molette)
    MIN_ZOOM = 0.2   # Zoom minimum (20%)
    MAX_ZOOM = 3.0   # Zoom maximum (300%)
    dragging = False      # Vrai si on est en train de cliquer-déplacer
    drag_last_pos = (0, 0)  
    # --- 2. INITIALISATION ---
    pygame.init()

    # --- 3. CHARGEMENT DE L'IMAGE ---
    try:
        #  On charge l'image ORIGINALE (très important)
        original_map_image = pygame.image.load(CHEMIN_IMAGE_MAP)
    except pygame.error as e:
        print(f"ERREUR FATALE : Impossible de charger l'image : {CHEMIN_IMAGE_MAP}")
        print(f"Détail Pygame : {e}")
        pygame.quit()
        sys.exit()

    # --- 4. CRÉATION DE LA FENÊTRE ---
    # On garde la taille de base de l'image pour la fenêtre
    width, height = original_map_image.get_size()
    screen = pygame.display.set_mode((width, height))
    #  On récupère le rectangle de l'écran pour centrer l'image
    screen_rect = screen.get_rect() 
    pygame.display.set_caption("Ma Carte (Molette pour zoomer, Espace pour quitter)")

    # --- 5. OPTIMISATION ET VARIABLES DE ZOOM ---
    original_map_image = original_map_image.convert()

    current_scale = 1.0  #  Le zoom commence à 1.0 (100%)
    #  L'image qu'on va dessiner (commence comme une copie de l'originale)
    current_map_image = original_map_image.copy()
    current_map_rect = current_map_image.get_rect(center=screen_rect.center)

    # --- 6. BOUCLE DE JEU ---
    running = True
    while running:

        # Gère les actions de l'utilisateur (événements)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    running = False
            
            #  DÉTECTION DE LA MOLETTE
            if event.type == pygame.MOUSEWHEEL:
                # event.y == 1 (molette vers le haut, zoomer)
                # event.y == -1 (molette vers le bas, dézoomer)
                current_scale += event.y * ZOOM_STEP
                
                #  Limiter le zoom
                current_scale = max(MIN_ZOOM, min(current_scale, MAX_ZOOM))
                
                #  Calculer la nouvelle taille
                new_width = int(original_map_image.get_width() * current_scale)
                new_height = int(original_map_image.get_height() * current_scale)
                
                #  Créer la nouvelle image zoomée (depuis l'originale !)
                current_map_image = pygame.transform.scale(original_map_image, (new_width, new_height))
                
                #  Mettre à jour le rectangle de l'image en le centrant
                current_map_rect = current_map_image.get_rect(center=screen_rect.center)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # 1 = Clic gauche
                        dragging = True
                        drag_last_pos = event.pos # Mémorise où on a cliqué

        # 🆕 FIN DU CLIC
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            # 🆕 DÉPLACEMENT DE LA SOURIS
            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    # Calcule le delta (différence) de position
                    dx = event.pos[0] - drag_last_pos[0]
                    dy = event.pos[1] - drag_last_pos[1]
                    
                    # Applique le delta au rectangle de l'image
                    current_map_rect.x += dx
                    current_map_rect.y += dy
                    
                    # Met à jour la "dernière position" pour le prochain calcul
                    drag_last_pos = event.pos

        # Gère l'affichage

        # 🆕 Dessine l'image zoomée (ou non) à son emplacement centré
        screen.fill((0,0,0))
        screen.blit(current_map_image, current_map_rect)   
        # Met à jour l'écran
        pygame.display.flip()

    # --- 7. QUITTER ---
    pygame.quit()