"""File: soldat.py"""

import pygame


class Soldat(pygame.sprite.Sprite):
    
    instances = []  # Shared list for each object Soldat
        def __init__(self, name, hp, attack, armor, armor_pierce, range, vision_range, speed, reload, symbol="", position= (0,0),x, y, img_path):;
        super().__init__()
        self.name = name
        self.hp = hp
        self.attack = attack
        self.armor = armor
        self.armor_pierce = armor_pierce
        self.range = range
        self.vision_range = vision_range
        self.speed = speed
        self.reload = reload
        self.symbol = symbol


        Soldat.instances.append(self) # Adding the object to the shared list

        if img_path:
            self.image = pygame.image.load(img_path)
            self.rect = self.image.get_rect()
            self.rect.x = x * self.rect.width
            self.rect.y = y * self.rect.height


        self.is_alive = True     # It's true if the soldier has more than 0 HP.

    def __repr__(self):
        return (f"Unit(name={self.name}, hp={self.hp}, attack={self.attack}, armor={self.armor}, "
            f"armor_pierce={self.armor_pierce}, range={self.range}, vision_range={self.vision_range}, "
            f"speed={self.speed}, reload={self.reload}, symbol={self.symbol})")
    
    def __str__(self):
        return f"The {self.name} soldat have {self.hp}HP"

    def attack_target(self, target, map, enemy_player):
        if self.hp <= 0 or target.hp <= 0:
            raise ValueError("One of the units is already dead")
        if abs(self.position[0] - target.position[0]) > self.range or abs(self.position[1] - target.position[1]) > self.range:
            raise ValueError("Target is out of range")
        target.hp -= max(0, (self.attack - target.armor))
        if target.hp <= 0:
            target.hp = 0
            if isinstance(target, Unit):
                map.remove_unit(target)
                enemy_player.remove_unit(target)
            
        print(f"{self.name} attacked {target.name} for {max(0, (self.attack - target.armor))} damage")
        print(f"{target.name} has {target.hp} HP left")
    
    def move(self, dx, dy):
        pass
        
        
    
        
    


