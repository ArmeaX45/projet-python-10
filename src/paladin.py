"""File: paladin.py"""

from src.soldat import Soldat
import pygame

class Paladin(Soldat):
    
    def __init__(self, x=0, y=0 , team=0):
        # Team 1 (rouge): image statique
        # Team 0 (bleu): on charge le spritesheet
        if team == 1:
            image_path = "./assets/paladin_1.png"
            super().__init__(x=x, y=y, owner=team, img_path=image_path)
            self.frames = []
        else:
            # Team 0: Charger le spritesheet d'animation
            # On initialise d'abord sans image, puis on charge le spritesheet
            image_path = None
            super().__init__(x=x, y=y, owner=team, img_path=None)
            self.frames = []
            self._load_blue_spritesheet(x, y)

        self.img_path = image_path
        self.name = "Paladin"
        self.tag = "P"

        # Static Stats
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.armor = 2
        self.armor_pierce = 2
        self.attack_range = 0       # melee
        self.vision_range = 10
        self.speed = 2.1
        self.reload_time = 0.4
        
        self.frame_delay = 13
        self.attack_delay = 0.67
        
        # Boolean Stat
        self.is_close_combat = True

        # Bonus
        self.vs = {
            'Paladin' : -3,
            'Arbalester' : 8,
            'Halberdier' : -5
        }
        
        # Animation
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # Vitesse d'animation

    def _load_blue_spritesheet(self, grid_x, grid_y):
        """Charge le spritesheet du Paladin bleu."""
        try:
            # Charger le spritesheet: 1_RBs3JBPgP4sWcEmuhwzPMA.png
            spritesheet = pygame.image.load("./assets/1_RBs3JBPgP4sWcEmuhwzPMA.png").convert_alpha()
            sheet_w = spritesheet.get_width()   # 552
            sheet_h = spritesheet.get_height()  # 297
            
            # Configuration: 6 colonnes x 3 rangées
            cols = 6
            rows = 3
            frame_w = sheet_w // cols  # ~92
            frame_h = sheet_h // rows  # ~99
            
            # Taille finale du sprite (similaire aux autres unités ~32px)
            target_size = 32
            
            # Extraire les frames (on prend juste la première rangée pour l'animation de marche)
            for col in range(cols):
                frame_rect = pygame.Rect(col * frame_w, 0, frame_w, frame_h)
                frame_surface = spritesheet.subsurface(frame_rect).copy()
                
                # Redimensionner proprement
                scaled_frame = pygame.transform.smoothscale(frame_surface, (target_size, target_size))
                self.frames.append(scaled_frame)
            
            # Configurer l'image initiale et le rect
            if self.frames:
                self.image = self.frames[0]
                self.rect = self.image.get_rect()
                # Position sur la grille
                self.rect.x = grid_x * target_size
                self.rect.y = grid_y * target_size
                self.exact_x = float(self.rect.x)
                self.exact_y = float(self.rect.y)
            else:
                raise Exception("Aucune frame chargée")
                
        except Exception as e:
            print(f"Erreur chargement spritesheet Paladin bleu: {e}")
            # Fallback: rectangle bleu
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.image.fill((50, 50, 200))
            self.rect = self.image.get_rect()
            self.rect.x = grid_x * 32
            self.rect.y = grid_y * 32
            self.exact_x = float(self.rect.x)
            self.exact_y = float(self.rect.y)
            self.frames = []
    
    def update_animation(self):
        """Met à jour l'animation du Paladin bleu."""
        if not self.frames:
            return
        
        self.animation_timer += 1
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]