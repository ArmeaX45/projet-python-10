import pygame


"""File: soldat.py"""
class Soldat(pygame.sprite.Sprite):
    
    def __init__(self, img_path):
        
        super().__init__()
        
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect()
        
    
    def attack(self):
        pass
    
    def move(self):
        pass
    
        
    


