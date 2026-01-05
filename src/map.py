"""File: map.py"""

import pygame
import sys

class Map:
    def __init__(self, image_path, screen_rect):
        self.image_path = image_path
        # --- CONFIGURATION DU ZOOM ---
        self.ZOOM_STEP = 0.08
        self.MIN_ZOOM = 0.2
        self.MAX_ZOOM = 3.0

        # --- CHARGEMENT DE L'IMAGE ---
        try:
            self.original_image = pygame.image.load(image_path).convert()
        except pygame.error as e:
            print(f"ERREUR : Impossible de charger l'image : {image_path}")
            sys.exit()

        # --- VARIABLES D'ÉTAT ---
        self.current_scale = 1.0
        self.image = self.original_image.copy()
        # On centre la carte au départ par rapport à l'écran
        self.rect = self.image.get_rect(center=screen_rect.center)

        #define de la mini map
        self.mm_ratio = 0.05 
        self.mm_img = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * self.mm_ratio), int(self.original_image.get_height() * self.mm_ratio)))
        # Gestion du Drag & Drop
        self.dragging = False
        self.drag_last_pos = (0, 0)

    def mouvement(self, event):
        """Gère les événements liés à la map (Zoom et Déplacement)."""
        
        # --- GESTION DU ZOOM (MOLETTE) ---
        if event.type == pygame.MOUSEWHEEL:
            old_scale = self.current_scale
            self.current_scale += event.y * self.ZOOM_STEP
            self.current_scale = max(self.MIN_ZOOM, min(self.current_scale, self.MAX_ZOOM))
            
            # Recalcul de la taille de l'image
            new_width = int(self.original_image.get_width() * self.current_scale)
            new_height = int(self.original_image.get_height() * self.current_scale)
            
            # Mise à jour de l'image affichée
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            
            # On conserve le centre actuel pour que le zoom soit fluide
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
        
        # --- GESTION DU DRAG & DROP ---
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clic gauche
                self.dragging = True
                self.drag_last_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.drag_last_pos[0]
                dy = event.pos[1] - self.drag_last_pos[1]
                self.rect.x += dx
                self.rect.y += dy
                self.drag_last_pos = event.pos

    def draw(self, screen):
        """Dessine la map principale et la minimap avec gestion des bords."""
        # 1. Dessiner la carte principale (Zoomée/Déplacée)
        screen.blit(self.image, self.rect)

        # --- GESTION DE LA MINIMAP ---
        margin = 20
        mm_w = self.mm_img.get_width()
        mm_h = self.mm_img.get_height()
        
        # Position : Haut-Droite
        mm_x = screen.get_width() - mm_w - margin
        mm_y = margin
        
        # Rectangle contenant la minimap (pour les calculs de collision)
        minimap_rect = pygame.Rect(mm_x, mm_y, mm_w, mm_h)

        # Dessiner un fond noir et une bordure blanche autour de la minimap pour bien la délimiter
        pygame.draw.rect(screen, (0, 0, 0), (mm_x - 2, mm_y - 2, mm_w + 4, mm_h + 4)) # Fond noir
        pygame.draw.rect(screen, (255, 255, 255), (mm_x - 2, mm_y - 2, mm_w + 4, mm_h + 4), 1) # Bord blanc fin
        
        # Dessiner l'image de la minimap
        screen.blit(self.mm_img, (mm_x, mm_y))
        
        # --- CALCUL DU CADRE ROUGE (VIEWPORT) ---
     
        view_world_x = -self.rect.x / self.current_scale
        view_world_y = -self.rect.y / self.current_scale
        view_world_w = screen.get_width() / self.current_scale
        view_world_h = screen.get_height() / self.current_scale
        
        # On convertit ces coordonnées "monde" en coordonnées "minimap"
        rx = mm_x + (view_world_x * self.mm_ratio)
        ry = mm_y + (view_world_y * self.mm_ratio)
        rw = view_world_w * self.mm_ratio
        rh = view_world_h * self.mm_ratio
        
        view_rect = pygame.Rect(rx, ry, rw, rh)
        
    
        final_rect = view_rect.clip(minimap_rect)
        
        # On ne dessine que si le rectangle a une taille valide
        if final_rect.width > 0 and final_rect.height > 0:
            pygame.draw.rect(screen, (255, 0, 0), final_rect, 2)

    def nouvelle_map(self, world_x, world_y):
        """
        Convertit une position 'monde' (position réelle sur l'image originale)
        en position 'écran' (prenant en compte le zoom et le déplacement).
        """
        screen_x = self.rect.x + (world_x * self.current_scale)
        screen_y = self.rect.y + (world_y * self.current_scale)
        return screen_x, screen_y