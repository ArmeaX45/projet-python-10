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
        """Dessine la map sur l'écran."""
        screen.blit(self.image, self.rect)

        # Position de la minimap (Haut-Droite avec marge de 20px)
        mx, my = screen.get_width() - self.mm_img.get_width() - 20, 20
        screen.blit(self.mm_img, (mx, my))
        
        vx = (-self.rect.x / self.current_scale) * self.mm_ratio
        vy = (-self.rect.y / self.current_scale) * self.mm_ratio
        vw = (screen.get_width() / self.current_scale) * self.mm_ratio
        vh = (screen.get_height() / self.current_scale) * self.mm_ratio
        # Définit le rectangle rouge théorique
        view_rect = pygame.Rect(mx + vx, my + vy, vw, vh)
        # Définit le rectangle limite (la minimap)
        limit_rect = pygame.Rect(mx, my, self.mm_img.get_width(), self.mm_img.get_height())
        
        # Dessine l'intersection des deux (le clip)
        pygame.draw.rect(screen, (255, 0, 0), view_rect.clip(limit_rect), 2)

    def nouvelle_map(self, world_x, world_y):
        """
        Convertit une position 'monde' (position réelle sur l'image originale)
        en position 'écran' (prenant en compte le zoom et le déplacement).
        """
        screen_x = self.rect.x + (world_x * self.current_scale)
        screen_y = self.rect.y + (world_y * self.current_scale)
        return screen_x, screen_y