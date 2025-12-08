# main.py
import pygame
import sys
from src.ai_daft import MajorDaftSimple
# Import de ta nouvelle classe Map
from src.map import Map 
from src.game import Game 

# Import des unités
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

if __name__ == "__main__":
    # --- 1. INITIALISATION ---
    pygame.init()
    ia_ennemie = MajorDaftSimple(team_name=1)
    # On définit une taille d'écran (tu peux ajuster ou rendre dynamique)
    SCREEN_WIDTH = 1900
    SCREEN_HEIGHT = 1000
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Map Zoomable avec Soldat (Refactorisé)")
    
    # --- 2. CRÉATION DE LA MAP ---
    game_map = Map("./assets/image.png", screen.get_rect())
    game = Game()
    # --- 3. CRÉATION DES UNITÉS ---
    tous_mes_soldats = (
        [{"soldat": Halberdier(x, y, 0)} for x in range(0, 10) for y in range(0, 10)] +
        [{"soldat": Paladin(x, y, 1)} for x in range(0, 10) for y in range(10, 20)] +
        [{"soldat": Arbalester(x, y, 1)} for x in range(10, 20) for y in range(0, 10)]
    )

    # --- 4. BOUCLE DE JEU ---
    running = True
    clock = pygame.time.Clock()

    # vie du sprite : 
    pygame.font.init()
    font = pygame.font.SysFont(None, 40) # Police taille 40
    soldat_selectionne = None
    #vie du sprite fin

    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11: # Petite touche pour quitter proprement aussi
                    running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # Clic Droit
                soldat_selectionne = None # On reset si on clique dans le vide
                for s in tous_mes_soldats:
                    unit = s["soldat"]
                    sx, sy = game_map.nouvelle_map(unit.rect.x, unit.rect.y)
                    w, h = unit.rect.width * game_map.current_scale, unit.rect.height * game_map.current_scale
                    
                    if pygame.Rect(sx, sy, w, h).collidepoint(event.pos):
                        soldat_selectionne = unit
                        break
            
            # La classe map gère les actions possibles sur la map
            game_map.mouvement(event)
        # --- IA ---
        # 1. L'IA réfléchit en lisant ta liste de dictionnaires
        actions = ia_ennemie.update(tous_mes_soldats)

        # 2. On applique les actions
        for action_type, unit, *args in actions:
            if action_type == "move":
                dx, dy = args[0], args[1]
                # On utilise ta map pour valider le mouvement
                unit.move(game, dx, dy)
            
            elif action_type == "attack":
                target = args[0]
                unit.attack(target)

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
        

        # 5) Affichage          
        pygame.display.flip()
        clock.tick(60) 

    pygame.quit()
    sys.exit()
