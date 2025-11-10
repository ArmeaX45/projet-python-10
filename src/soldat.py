# src/soldat.py (ajouts ciblés)
import pygame

class Soldat(pygame.sprite.Sprite):
    instances = []

    def __init__(self, x, y, img_path, owner: int = 0):
        super().__init__()
        Soldat.instances.append(self)

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
        armor = soldat.armor if self.is_close_combat else soldat.armor_pierce
        damage = self.damage
        if soldat.name in self.vs:
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
        if dx != 0:
            new_x = self.rect.x + dx * self.rect.width * self.speed
            if 0 <= new_x < map.width * self.rect.width:    #Ajout <=
                self.rect.x += dx * self.rect.width * self.speed
                grid_x = self.rect.x // self.rect.width
            elif 0 < new_x:
                self.rect.x = 0
            elif new_x < map.width * self.rect.width:
                self.rect.x = map.width * self.rect.width - self.rect.width

        if dy != 0:
            new_y = self.rect.y + dy * self.rect.height * self.speed
            if 0 <= new_y < map.height *  self.rect.height:   #Ajout <=
                self.rect.y = new_y
                grid_y = self.rect.y // self.rect.height
            elif 0 < new_y:
                self.rect.y = 0
            elif new_y < map.height * self.rect.height:
                self.rect.y = map.height * self.rect.height - self.rect.height

        map.grid[grid_y][grid_x] = self.tag
        

        """
        def can_attack(self, other: "Soldat") -> bool:
        if not other or not other.is_alive:
            return False
        x, y = self.tile_pos()
        ox, oy = other.tile_pos()
        dx, dy = x - ox, y - oy
        return (dx*dx + dy*dy) <= (max(0, self.attack_range) ** 2)
        """
        
        
            
        
        
        
    
        
    


