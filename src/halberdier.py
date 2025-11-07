"""File: halberdier.py"""

from src.soldat import Soldat

import pygame


class Halberdier(Soldat):
    
    def __init__(self, name="Halberdier", hp=60, attack=6, armor=0, armor_pierce=0, range=0, vision_range=4, speed=1, reload=3.0, symbol="H", x=0, y=0, img_path="./assets/halberdier.png"):
        super().__init__(x=x, y=y, img_path=img_path)
        

        # Bonus
        # self.vs_arbalester = 0
        # self.vs_paladin = 32
        # self.vs_halberdier = 0
        self.vs = {
            'Paladin' : 32,
        }
