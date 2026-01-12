"""File: arbalester.py"""

from src.soldat import Soldat

class Arbalester(Soldat):
    
    def __init__(self, x=0, y=0, team=0):
        image_path =  "./assets/arbalester_1.png" if team==1 else "./assets/arbalester_0.png"
        super().__init__(x=x, y=y, img_path=image_path, owner=team)
        
        self.name = "Arbalester"
        self.tag = "A"

        # Static Stats
        self.hp = 35
        self.max_hp = 35
        self.damage = 5
        self.armor = 0
        self.armor_pierce = 0
        self.attack_range = 5
        self.vision_range = 7
        self.speed = 1.9
        self.reload_time = 0.6
        
        self.frame_delay = 15
        self.attack_delay = 0.35
        
        self.accuracy = 0.85        # 90%
        
        # Boolen Stat
        self.is_close_combat = False

        # Bonus
        # self.vs_arbalester = 0
        # self.vs_paladin = 0
        # self.vs_halberdier = 3
        self.vs = {
            'Halberdier' : 3,
        }