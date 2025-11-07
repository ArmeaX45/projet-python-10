"""File: arbalester.py"""

from src.soldat import Soldat

import pygame


class Arbalester(Soldat):
    
    def __init__(self, name="Arbalester", hp=40, attack=6, armor=0, armor_pierce=0, range=3, vision_range=7, speed=0.96, reload=2.0, symbol="A", x=0, y=0, img_path="./assets/arbalester.png"):
        super().__init__(x=x, y=y, img_path=img_path)
        
        self.frame_delay = 20
        self.attack_delay = 0.34
        
        self.accuracy = 0.90        # 90%

        # Bonus
        # self.vs_arbalester = 0
        # self.vs_paladin = 0
        # self.vs_halberdier = 3
        self.vs = {
            'Halberdier' : 3,
        }
