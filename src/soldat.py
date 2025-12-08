# src/soldat.py (ajouts ciblés)
import pygame


class Soldat(pygame.sprite.Sprite):

    def __init__(self, x, y, img_path, owner: int = 0):
        super().__init__()
        
        if img_path:
            self.image = pygame.image.load(img_path)
            self.rect = self.image.get_rect()
            self.rect.x = x * self.rect.width
            self.rect.y = y * self.rect.height
            
        self.is_alive = True     # It's true if the soldier has more than 0 HP.
        self.team = owner
        
        
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
            soldat.remove()
            
        
        print(f"{self.name} cause {damage} at {soldat.name}")
        
        return None
    
    
    def can_move(self, map, new_x=None, new_y=None):
        for soldat in map.all_soldats:

            if soldat is self:
                continue

            # Mouvement diagonal
            if new_x is not None and new_y is not None:
                if soldat.rect.x == new_x and soldat.rect.y == new_y:
                    return False

            # Mouvement horizontal
            if new_x is not None:
                if soldat.rect.y == self.rect.y and soldat.rect.x == new_x:
                    return False

            # Mouvement vertical
            if new_y is not None:
                if soldat.rect.x == self.rect.x and soldat.rect.y == new_y:
                    return False
                
        return True

    
    
    def move(self, map, dx=None, dy=None):
        
        with map.lock:
        
            grid_x = self.rect.x // self.rect.width
            grid_y = self.rect.y // self.rect.height
            
            map.grid[grid_y][grid_x] = '-'
            if dx !=0 and dx:
                new_x = self.rect.x + dx * self.rect.width * self.speed
                if self.can_move(map=map, new_x=new_x):
                    if 0 <= new_x <= map.width * self.rect.width:
                        self.rect.x += dx * self.rect.width * self.speed
                        grid_x = self.rect.x // self.rect.width
                    elif 0 < new_x:
                        self.rect.x = 0
                    elif new_x < map.width * self.rect.width:
                        self.rect.x = map.width * self.rect.width - self.rect.width

            if dy != 0 and dy:
                new_y = self.rect.y + dy * self.rect.height * self.speed
                if self.can_move(map=map, new_y=new_y):
                    if 0 <= new_y <= map.height *  self.rect.height:
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
            
        
        
            
        
        
        
    
        
    


