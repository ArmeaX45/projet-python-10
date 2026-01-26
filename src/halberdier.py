"""File: halberdier.py"""

from src.soldat import Soldat

import pygame


class Halberdier(Soldat):
    
    def __init__(self, x=0, y=0, team=0):
<<<<<<< HEAD
        image_path =  "./assets/halbardier_1.png" if team==1 else "./assets/harbaldier_0.png"

        super().__init__(x=x, y=y, owner=team, img_path=image_path)
=======
        if team == 1:
            image_path = "./assets/PikemanRedWalk/Pikemanwalk"
            super().__init__(x=x, y=y, owner=team, img_path=None)
            self.frames = []
            self.load_animation_frames(x, y, image_path)
        else:
            # Team 0: Charger le spritesheet d'animation
            # On initialise d'abord sans image, puis on charge le spritesheet
            image_path = "./assets/PikemanBleuWalk/Pikemanwalk"
            super().__init__(x=x, y=y, owner=team, img_path=None)
            self.frames = []
            self.load_animation_frames(x, y, image_path)
            
    
>>>>>>> Noah
        self.img_path = image_path
        self.name = "Halberdier"
        self.tag = "H"
        self.frames = []
        # Static Stats
        self.hp = 55
        self.max_hp = 55
        self.damage = 4
        self.armor = 0
        self.armor_pierce = 0
        self.attack_range = 0       
        self.vision_range = 4
        self.speed = 2.0
        self.reload_time = 0.5

        self.is_close_combat = True
        

        self.vs = {
            'Paladin' : 10,
            'Arbalester' : -3,
            'Halberdier' : 0
<<<<<<< HEAD
        }
=======
        }
        
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # Vitesse d'animation
        
    def load_animation_frames(self, x, y, image_path):
        """Charge les frames d'animation pour le pikeman."""
        images = []
        path = image_path
        
        for num in range(1, 5):
            img_path = f"{path}{num}.png"
            images.append(pygame.image.load(img_path))
            
        self.frames = images
        self.image = self.frames[0]  # Initialiser avec la première frame
        self.rect = self.image.get_rect()
        # Position sur la grille
        self.rect.x = x * 32
        self.rect.y = y * 32
        self.exact_x = float(self.rect.x)
        self.exact_y = float(self.rect.y)
>>>>>>> Noah
