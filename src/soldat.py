"""File: soldat.py"""

import pygame


class Soldat(pygame.sprite.Sprite):
    
    instances = []  # Shared list for each object Soldat
    
    def __init__(self, x, y, img_path):
        
        super().__init__()
        Soldat.instances.append(self) # Adding the object to the shared list

        if img_path:
            self.image = pygame.image.load(img_path)
            self.rect = self.image.get_rect()
            self.rect.x = x * self.rect.width
            self.rect.y = y * self.rect.height

        
        self.is_alive = True     # It's true if the soldier has more than 0 HP.
        
    def __str__(self):
        return f"The {self.name} soldat have {self.hp}HP"
    
    def attack(self, soldat):
        armor = soldat.armor if self.is_close_combat else soldat.armor_pierce   # Select the type of armour to use
        
        damage = self.damage
        if soldat.name in self.vs:                   # Bonus Damage ?
            damage = self.damage + self.vs[soldat.name]
        
        soldat.hp -= max(0, (damage - armor))
        
        print(f"{self.name} cause {damage} at {soldat.name}")
        
        return None
    
    def move(self, dx, dy):
        pass
        
        
    
        
    


