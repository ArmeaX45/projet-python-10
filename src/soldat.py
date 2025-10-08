import pygame


"""File: soldat.py"""
class Soldat(pygame.sprite.Sprite):
    
    def __init__(self, img_path):
        
        super().__init__()
        
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect()
        
        
        self.is_alive = True     # It's true if the soldier has more than 0 HP.
          
    
    def attack(self, soldat):
        armor = soldat.armor if self.is_close_combat else soldat.armor_pierce   # Select the type of armour to use
        
        damage = self.damage
        if soldat.name in self.vs.keys():                   # Bonus Damage ?
            damage = self.damage + self.vs[soldat.name]
        
        soldat.hp -= (damage - armor)
        return None
    
    def move(self):
        pass
    
        
    


