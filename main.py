# main.py
import pygame
import sys

# Import de ta nouvelle classe Map
from src.map import Map 

# Import des unités
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

if __name__ == "__main__":
    # --- 1. INITIALISATION ---
    pygame.init()
    
    # On définit une taille d'écran (tu peux ajuster ou rendre dynamique)
    SCREEN_WIDTH = 1900
    SCREEN_HEIGHT = 1000
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Map Zoomable avec Soldat (Refactorisé)")
    
    # --- 2. CRÉATION DE LA MAP ---
    # On passe le rectangle de l'écran pour centrer la map au départ
    game_map = Map("image.png", screen.get_rect())

    # --- 3. CRÉATION DES UNITÉS ---
    # Note: J'ai gardé ta structure de liste de dictionnaires
    tous_mes_soldats = (
        [{"soldat": Halberdier(x, y, 1)} for x in range(0, 10) for y in range(0, 10)] +
        [{"soldat": Paladin(x, y, 1)} for x in range(0, 10) for y in range(10, 20)] +
        [{"soldat": Arbalester(x, y, 1)} for x in range(10, 20) for y in range(0, 10)]
    )

    # --- 4. BOUCLE DE JEU ---
    running = True
    clock = pygame.time.Clock()

    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11: # Petite touche pour quitter proprement aussi
                    running = False
            
            # On délègue la gestion des inputs map à la classe Map
            game_map.handle_input(event)

        # Affichage
        screen.fill((0, 0, 0))

        #  Dessiner la map
        game_map.draw(screen)

        #  Dessiner les soldats
        current_scale = game_map.current_scale # Récupérer le scale pour redimensionner les sprites

        for s in tous_mes_soldats:
            unit = s["soldat"]
            
            # Position réelle 
            world_x = unit.rect.x
            world_y = unit.rect.y

            # Conversion vers Position Écran via la classe Map
            screen_x, screen_y = game_map.world_to_screen(world_x, world_y)

            # Redimensionnement du sprite selon le zoom actuel
            soldat_w = int(unit.rect.width * current_scale)
            soldat_h = int(unit.rect.height * current_scale)
            
            #  vérifie que la taille est valide pour éviter les crashs si zoom  petit
            if soldat_w > 0 and soldat_h > 0:
                soldat_scaled_img = pygame.transform.scale(unit.image, (soldat_w, soldat_h))
                screen.blit(soldat_scaled_img, (screen_x, screen_y))

        pygame.display.flip()
        clock.tick(60) 

    pygame.quit()
    sys.exit()