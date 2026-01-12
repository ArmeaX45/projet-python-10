"""File: halberdier.py"""

from src.soldat import Soldat

import pygame


class Halberdier(Soldat):
    
    def __init__(self, x=0, y=0, team=0):
        image_path =  "./assets/halbardier_1.png" if team==1 else "./assets/harbaldier_0.png"

        super().__init__(x=x, y=y, owner=team, img_path=image_path)
        self.name = "Halberdier"
        self.tag = "H"
     
        # Static Stats
        self.hp = 55
        self.max_hp = 55
        self.damage = 4
        self.armor = 0
        self.armor_pierce = 0
        self.attack_range = 0       # melee
        self.vision_range = 4
        self.speed = 2.0
        self.reload_time = 0.5

        # Boolen Stat
        self.is_close_combat = True
        

        # Bonus
        # self.vs_arbalester = 0
        # self.vs_paladin = 32
        # self.vs_halberdier = 0
        self.vs = {
            'Paladin' : 22,
            'Arbalester' : -5,
            'Halberdier' : 0
        }