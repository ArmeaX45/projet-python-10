"""File: halberdier.py"""

from src.soldat import Soldat

import pygame


class Halberdier(Soldat):
    
    def __init__(self, x=0, y=0, img_path="./assets/halberdier.png"):
        super().__init__(x=x, y=y, img_path=img_path)

        self.name = "Halberdier"
        self.tag = "H"
        
        # Stats
        self.hp = 60
        self.damage = 6
        self.armor = 0
        self.armor_pierce = 0
        self.attack_range = 0       # melee
        self.vision_range = 4
        self.speed = 1.0
        self.reload_time = 3.0

        # Boolen Stat
        self.is_close_combat = True
        

        # Bonus
        # self.vs_arbalester = 0
        # self.vs_paladin = 32
        # self.vs_halberdier = 0
        self.vs = {
            'Paladin' : 32,
        }