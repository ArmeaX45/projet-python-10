import pygame


"""File: soldat.py"""
class Soldat(pygame.sprite.Sprite):
    
    def __init__(self, img_path):
        
        super().__init__()

        img_path = None     # To remove when we will have the good assets
        if img_path:
            self.image = pygame.image.load(img_path)
            self.rect = self.image.get_rect()
        
        
        self.is_alive = True     # It's true if the soldier has more than 0 HP.
        
    def __repr__(self):
        return f"The {self.name} soldat have {self.hp}HP"
    
    def attack(self, soldat):
        armor = soldat.armor if self.is_close_combat else soldat.armor_pierce   # Select the type of armour to use
        
        damage = self.damage
        if soldat.name in self.vs:                   # Bonus Damage ?
            damage = self.damage + self.vs[soldat.name]
        
        soldat.hp -= (damage - armor)
        
        print(f"{self.name} cause {damage} at {soldat.name}")
        
        return None
    
    def move(self):
        pass
    
        
    


