"""File: paladin.py"""

from src.soldat import Soldat

import pygame


class Paladin(Soldat):
    
    def __init__(self, name="Paladin", hp=160, attack=14, armor=2, armor_pierce=3, range=0, vision_range=5, speed=1.35, reload=1.9, symbol="P",x=0, y=0, img_path="./assets/paladin.png"):
        super().__init__(x=x, y=y, img_path=img_path)
        
        self.frame_delay = 13
        self.attack_delay = 0.67

        # Bonus
        # self.vs_arbalester = 0
        # self.vs_paladin = -3
        # self.vs_halberdier = 0
        self.vs = {
            'Paladin' : -3,
        }
        
