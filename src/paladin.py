from src.soldat import Soldat
import pygame


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE PALADIN : Unité de combat lourde avec haute résistance
# Bonus contre les Arbalétriers, faible contre les Hallebardiers
# ═══════════════════════════════════════════════════════════════════════════════
class Paladin(Soldat):
    
    def __init__(self, x=0, y=0 , team=0):
        if team == 1:
            image_path = "./assets/paladin_1.png"
            super().__init__(x=x, y=y, owner=team, img_path=image_path)
            self.frames = []
        else:
            image_path = None
            super().__init__(x=x, y=y, owner=team, img_path=None)
            self.frames = []
            self._load_blue_spritesheet(x, y)

        self.img_path = image_path
        self.name = "Paladin"
        self.tag = "P"

        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.armor = 2
        self.armor_pierce = 2
        self.attack_range = 0
        self.vision_range = 10
        self.speed = 2.1
        self.reload_time = 0.4
        
        self.frame_delay = 13
        self.attack_delay = 0.67
        self.is_close_combat = True

        self.vs = {
            'Paladin' : -3,
            'Arbalester' : 7,
            'Halberdier' : -5
        }
        
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5


    # ═══════════════════════════════════════════════════════════════════════════════
    # CHARGEMENT SPRITESHEET : Charge l'animation du Paladin bleu (équipe 0)
    # Découpe le spritesheet en 6 frames pour l'animation de marche
    # ═══════════════════════════════════════════════════════════════════════════════
    def _load_blue_spritesheet(self, grid_x, grid_y):
        try:
            spritesheet = pygame.image.load("./assets/1_RBs3JBPgP4sWcEmuhwzPMA.png").convert_alpha()
            sheet_w = spritesheet.get_width()
            sheet_h = spritesheet.get_height()
            
            cols = 6
            rows = 3
            frame_w = sheet_w // cols
            frame_h = sheet_h // rows
            target_size = 32
            
            for col in range(cols):
                frame_rect = pygame.Rect(col * frame_w, 0, frame_w, frame_h)
                frame_surface = spritesheet.subsurface(frame_rect).copy()
                scaled_frame = pygame.transform.smoothscale(frame_surface, (target_size, target_size))
                self.frames.append(scaled_frame)
            
            if self.frames:
                self.image = self.frames[0]
                self.rect = self.image.get_rect()
                self.rect.x = grid_x * target_size
                self.rect.y = grid_y * target_size
                self.exact_x = float(self.rect.x)
                self.exact_y = float(self.rect.y)
            else:
                raise Exception("Aucune frame chargée")
                
        except Exception as e:
            print(f"Erreur chargement spritesheet Paladin bleu: {e}")
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.image.fill((50, 50, 200))
            self.rect = self.image.get_rect()
            self.rect.x = grid_x * 32
            self.rect.y = grid_y * 32
            self.exact_x = float(self.rect.x)
            self.exact_y = float(self.rect.y)
            self.frames = []


