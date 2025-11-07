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
        self.team = None
        
        
    def __str__(self):
        return f"The {self.name} soldat have {self.hp}HP"
    
    
    def attack(self, soldat):
        armor = soldat.armor if self.is_close_combat else soldat.armor_pierce   # Select the type of armour to use
        
        damage = self.damage
        if soldat.name in self.vs:                   # Bonus Damage ?
            damage = self.damage + self.vs[soldat.name]
        
        soldat.hp -= damage - armor
        
        if soldat.hp <= 0:
            soldat.is_alive = False
            
        
        print(f"{self.name} cause {damage} at {soldat.name}")
        
        return None
    
    
    def move(self,map, dx=None, dy=None):
        
        grid_x = self.rect.x // self.rect.width
        grid_y = self.rect.y // self.rect.height
        
        map.grid[grid_y][grid_x] = '-'
        if dx:
            new_x = self.rect.x + dx * self.rect.width * self.speed
            if 0 < new_x < map.width * self.rect.width:
                self.rect.x += dx * self.rect.width * self.speed
                grid_x = self.rect.x // self.rect.width
            elif 0 < new_x:
                self.rect.x = 0
            elif new_x < map.width * self.rect.width:
                self.rect.x = map.width * self.rect.width - self.rect.width

        else:
            new_y = self.rect.y + dy * self.rect.height * self.speed
            if 0 < new_y < map.height *  self.rect.height:
                self.rect.y = new_y
                grid_y = self.rect.y // self.rect.height
            elif 0 < new_y:
                self.rect.y = 0
            elif new_y < map.height * self.rect.height:
                self.rect.y = map.height * self.rect.height - self.rect.height

        map.grid[grid_y][grid_x] = self.tag
        
        
        
            
        
        
        
    
        
    


