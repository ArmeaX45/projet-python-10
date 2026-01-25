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

        # --- MINIMAP AVEC TAILLE FIXE GARANTIE ---
        self.MINIMAP_WIDTH = 300
        self.MINIMAP_HEIGHT = 170
        
        # Calculer le scale pour conserver les proportions
        orig_w = self.original_image.get_width()
        orig_h = self.original_image.get_height()
        
        # Ratio de l'image originale
        aspect = orig_w / orig_h
        
        # Adapter à la box 300x170 en conservant les proportions
        if aspect > (self.MINIMAP_WIDTH / self.MINIMAP_HEIGHT):
            # Image plus large que haute -> limiter par la largeur
            self.mm_w = self.MINIMAP_WIDTH
            self.mm_h = int(self.MINIMAP_WIDTH / aspect)
        else:
            # Image plus haute que large -> limiter par la hauteur  
            self.mm_h = self.MINIMAP_HEIGHT
            self.mm_w = int(self.MINIMAP_HEIGHT * aspect)
        
        # Scale pour convertir coordonnées monde -> minimap
        self.minimap_scale = self.mm_w / orig_w
        
        # Image de minimap pré-calculée avec smoothscale (meilleure qualité)
        self.mm_img = pygame.transform.smoothscale(self.original_image, (self.mm_w, self.mm_h))
        
        print(f"[DEBUG MINIMAP] Taille: {self.mm_w}x{self.mm_h}, Scale: {self.minimap_scale}")
        
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
        """Dessine uniquement la carte principale (fond)."""
        screen.blit(self.image, self.rect)

    def draw_minimap(self, screen):
        """Dessine la minimap avec le cadre rouge du viewport. À appeler APRÈS les soldats."""
        margin = 20
        
        # Position en haut à droite
        mm_x = screen.get_width() - self.mm_w - margin
        mm_y = margin
        
        # Fond noir avec bordure épaisse pour bien voir
        border = 4
        pygame.draw.rect(screen, (0, 0, 0), (mm_x - border, mm_y - border, self.mm_w + border*2, self.mm_h + border*2))
        pygame.draw.rect(screen, (255, 255, 255), (mm_x - border, mm_y - border, self.mm_w + border*2, self.mm_h + border*2), 3)
        
        # Dessiner la minimap (image pré-calculée)
        screen.blit(self.mm_img, (mm_x, mm_y))
        
        # --- CADRE ROUGE (VIEWPORT) ---
        view_world_x = -self.rect.x / self.current_scale
        view_world_y = -self.rect.y / self.current_scale
        view_world_w = screen.get_width() / self.current_scale
        view_world_h = screen.get_height() / self.current_scale
        
        # Conversion en coordonnées minimap
        rx = mm_x + (view_world_x * self.minimap_scale)
        ry = mm_y + (view_world_y * self.minimap_scale)
        rw = view_world_w * self.minimap_scale
        rh = view_world_h * self.minimap_scale
        
        # Limiter le rectangle aux bords de la minimap
        minimap_rect = pygame.Rect(mm_x, mm_y, self.mm_w, self.mm_h)
        view_rect = pygame.Rect(rx, ry, rw, rh)
        final_rect = view_rect.clip(minimap_rect)
        
        # Dessiner le cadre rouge épais
        if final_rect.width > 0 and final_rect.height > 0:
            pygame.draw.rect(screen, (255, 0, 0), final_rect, 3)

    def nouvelle_map(self, world_x, world_y):
        """
        Convertit une position 'monde' (position réelle sur l'image originale)
        en position 'écran' (prenant en compte le zoom et le déplacement).
        """
        screen_x = self.rect.x + (world_x * self.current_scale)
        screen_y = self.rect.y + (world_y * self.current_scale)
        return screen_x, screen_y