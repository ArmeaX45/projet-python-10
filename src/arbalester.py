"""File: arbalester.py"""

from src.soldat import Soldat

import pygame


class Arbalester(Soldat):
    
    def __init__(self, x=0, y=0, img_path="./assets/arbalester.png"):
        super().__init__(x=x, y=y, img_path=img_path)
        
        self.name = "Arbalester"
        self.tag = "A"

        # Static Stats
        self.hp = 40
        self.damage = 6
        self.armor = 0
        self.armor_pierce = 0
        self.attack_range = 5
        self.vision_range = 7
        self.speed = 0.96
        self.reload_time = 2.0
        
        self.frame_delay = 20
        self.attack_delay = 0.34
        
        self.accuracy = 0.90        # 90%
        
        # Boolen Stat
        self.is_close_combat = False

        # Bonus
        # self.vs_arbalester = 0
        # self.vs_paladin = 0
        # self.vs_halberdier = 3
        self.vs = {
            'Halberdier' : 3,
        }