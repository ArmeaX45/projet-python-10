"""File: paladin.py"""

from src.soldat import Soldat

class Paladin(Soldat):
    
    def __init__(self, x=0, y=0 , team=0):
        image_path="./assets/paladin_1.png" if team==1 else "./assets/paladin_0.png"
        super().__init__(x=x, y=y, owner=team, img_path=image_path)

        self.name = "Paladin"
        self.tag = "P"

        # Static Stats
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.armor = 2
        self.armor_pierce = 2
        self.attack_range = 0       # melee
        self.vision_range = 20
        self.speed = 2.7
        self.reload_time = 0.4
        
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
        