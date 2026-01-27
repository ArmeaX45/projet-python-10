"""File: crossbowman .py"""

import pygame

from src.soldat import Soldat

class Crossbowman (Soldat):
    
    def __init__(self, x=0, y=0, team=0):
        
        # Team 1 (rouge): image statique
        # Team 0 (bleu): on charge le spritesheet
        if team == 1:
            image_path = f"./assets/ArlebestRedWalk/Arlebestwalk"
            super().__init__(x=x, y=y, owner=team, img_path=None)
            self.frames = []
            self.load_animation_frames(x, y, image_path)
        else:
            # Team 0: Charger le spritesheet d'animation
            # On initialise d'abord sans image, puis on charge le spritesheet
            image_path = f"./assets/ArlebestBleuWalk/Arlebestwalk"
            super().__init__(x=x, y=y, owner=team, img_path=None)
            self.frames = []
            self.load_animation_frames(x, y, image_path)       
        
        self.img_path = image_path
        self.name = "Crossbowman "
        self.tag = "A"

        # Static Stats
        self.hp = 35
        self.max_hp = 35
        self.damage = 5
        self.armor = 0
        self.armor_pierce = 0
        self.attack_range = 5
        self.vision_range = 7
        self.speed = 1.6
        self.reload_time = 0.6
        
        self.frame_delay = 15
        self.attack_delay = 0.35
        
        self.accuracy = 0.85        # 90%
        
        # Boolen Stat
        self.is_close_combat = False

        # Bonus

        self.vs = {
            'Pikeman' : 3,
        }
        
        # Animation
        self.frame = []
        
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # Vitesse d'animation
        
    def load_animation_frames(self, x, y, image_path):
        """Charge les frames d'animation pour l'Crossbowman ."""
        images = []
        path = image_path
        
        for num in range(1, 15):
            img_path = f"{path}{num}.png"
            images.append(pygame.image.load(img_path))
            
        self.frames = images
        self.image = self.frames[0]  # Initialiser avec la premiÃ¨re frame
        self.rect = self.image.get_rect()
        # Position sur la grille
        self.rect.x = x * 32
        self.rect.y = y * 32
        self.exact_x = float(self.rect.x)
        self.exact_y = float(self.rect.y)
        
    
            
        