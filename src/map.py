import pygame
import sys


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE MAP : Gère l'affichage de la carte, le zoom et le déplacement
# Inclut la minimap avec le viewport rouge pour la navigation
# ═══════════════════════════════════════════════════════════════════════════════
class Map:
    def __init__(self, image_path, screen_rect):
        self.image_path = image_path
        self.ZOOM_STEP = 0.08
        self.MIN_ZOOM = 0.2
        self.MAX_ZOOM = 3.0

        try:
            self.original_image = pygame.image.load(image_path).convert()
            w = self.original_image.get_width()
            h = self.original_image.get_height()
            self.original_image = pygame.transform.scale(self.original_image, (int(w * 1.5), int(h * 1.5)))
        except pygame.error as e:
            print(f"ERREUR : Impossible de charger l'image : {image_path}")
            sys.exit()

        self.current_scale = 1.0
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=screen_rect.center)

        self.MINIMAP_WIDTH = 300
        self.MINIMAP_HEIGHT = 170
        
        orig_w = self.original_image.get_width()
        orig_h = self.original_image.get_height()
        aspect = orig_w / orig_h
        
        if aspect > (self.MINIMAP_WIDTH / self.MINIMAP_HEIGHT):
            self.mm_w = self.MINIMAP_WIDTH
            self.mm_h = int(self.MINIMAP_WIDTH / aspect)
        else:
            self.mm_h = self.MINIMAP_HEIGHT
            self.mm_w = int(self.MINIMAP_HEIGHT * aspect)
        
        self.minimap_scale = self.mm_w / orig_w
        self.mm_img = pygame.transform.smoothscale(self.original_image, (self.mm_w, self.mm_h))
        
        print(f"[DEBUG MINIMAP] Taille: {self.mm_w}x{self.mm_h}, Scale: {self.minimap_scale}")
        
        self.dragging = False
        self.drag_last_pos = (0, 0)


    # ═══════════════════════════════════════════════════════════════════════════════
    # GESTION DES ÉVÉNEMENTS : Zoom avec molette et déplacement par drag & drop
    # Le zoom garde le centre de la vue, le drag déplace la carte
    # ═══════════════════════════════════════════════════════════════════════════════
    def mouvement(self, event):
        if event.type == pygame.MOUSEWHEEL:
            old_scale = self.current_scale
            self.current_scale += event.y * self.ZOOM_STEP
            self.current_scale = max(self.MIN_ZOOM, min(self.current_scale, self.MAX_ZOOM))
            
            new_width = int(self.original_image.get_width() * self.current_scale)
            new_height = int(self.original_image.get_height() * self.current_scale)
            
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
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
        screen.blit(self.image, self.rect)


    # ═══════════════════════════════════════════════════════════════════════════════
    # MINIMAP : Affiche une vue réduite de la carte avec le viewport actuel
    # Le rectangle rouge indique la zone actuellement visible à l'écran
    # ═══════════════════════════════════════════════════════════════════════════════
    def draw_minimap(self, screen):
        margin = 20
        
        mm_x = screen.get_width() - self.mm_w - margin
        mm_y = margin
        
        border = 4
        pygame.draw.rect(screen, (0, 0, 0), (mm_x - border, mm_y - border, self.mm_w + border*2, self.mm_h + border*2))
        pygame.draw.rect(screen, (255, 255, 255), (mm_x - border, mm_y - border, self.mm_w + border*2, self.mm_h + border*2), 3)
        
        screen.blit(self.mm_img, (mm_x, mm_y))
        
        view_world_x = -self.rect.x / self.current_scale
        view_world_y = -self.rect.y / self.current_scale
        view_world_w = screen.get_width() / self.current_scale
        view_world_h = screen.get_height() / self.current_scale
        
        rx = mm_x + (view_world_x * self.minimap_scale)
        ry = mm_y + (view_world_y * self.minimap_scale)
        rw = view_world_w * self.minimap_scale
        rh = view_world_h * self.minimap_scale
        
        minimap_rect = pygame.Rect(mm_x, mm_y, self.mm_w, self.mm_h)
        view_rect = pygame.Rect(rx, ry, rw, rh)
        final_rect = view_rect.clip(minimap_rect)
        
        if final_rect.width > 0 and final_rect.height > 0:
            pygame.draw.rect(screen, (255, 0, 0), final_rect, 3)


    # ═══════════════════════════════════════════════════════════════════════════════
    # CONVERSION COORDONNÉES : Transforme une position monde en position écran
    # Prend en compte le zoom actuel et le décalage de la carte
    # ═══════════════════════════════════════════════════════════════════════════════
    def nouvelle_map(self, world_x, world_y):
        screen_x = self.rect.x + (world_x * self.current_scale)
        screen_y = self.rect.y + (world_y * self.current_scale)
        return screen_x, screen_y