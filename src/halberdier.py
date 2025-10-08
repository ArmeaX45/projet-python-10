"""File: halberdier.py"""
from soldat import Soldat

import pygame


class Halberdier(Soldat):
    
    def __init__(self, img_path="asset/halberdier.png"):
        super().__init__(img_path=img_path)

        # Meta
        self.name = "Halberdier"

        self.hp = 60
        self.damage = 6
        self.armor = 0
        self.armor_pierce = 0
        self.attack_range = 0       # melee
        self.vision_range = 4
        self.speed = 1.0
        self.reload_time = 3.0


        # Bonus
        self.vs_arbalester = 0
        self.vs_paladin = 32
        self.vs_halberdier = 0