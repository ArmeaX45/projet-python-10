"""File: paladin.py"""

from src.soldat import Soldat

import pygame


class Paladin(Soldat):
    
    def __init__(self, x=0, y=0, img_path="./assets/paladin.png"):
        super().__init__(x=x, y=y, img_path=img_path)

        self.name = "Paladin"
        self.tag = "P"

        # Statsjknjn
        self.hp = 160
        self.damage = 14
        self.armor = 2
        self.armor_pierce = 3
        self.attack_range = 0       # melee
        self.vision_range = 5
        self.speed = 1.35
        self.reload_time = 1.9
        
        self.frame_delay = 13
        self.attack_delay = 0.67
        
        # Boolen Stat
        self.is_close_combat = True

        # Bonus
        # self.vs_arbalester = 0
        # self.vs_paladin = -3
        # self.vs_halberdier = 0
        self.vs = {
            'Paladin' : -3,
        }
        