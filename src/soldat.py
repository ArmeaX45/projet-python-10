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
    
    
    def can_move(self, game, new_x=None, new_y=None):

        future_rect = self.rect.copy()
        
        if new_x is not None:
            future_rect.x = new_x
        if new_y is not None:
            future_rect.y = new_y

        for soldat in game.all_soldats:
            if soldat is self:
                continue

            if future_rect.colliderect(soldat.rect):
                return False

        return True

    
    def move(self, game, dx=None, dy=None):
        
        with game.lock:
            # Calculer les nouvelles positions
            new_x = self.rect.x
            new_y = self.rect.y
            
            if dx != 0 and dx:
                new_x = self.rect.x + dx * self.rect.width * self.speed
                # Vérifier les limites de la carte
                if new_x < 0:
                    new_x = 0
                elif new_x > game.width * self.rect.width - self.rect.width:
                    new_x = game.width * self.rect.width - self.rect.width
            
            if dy != 0 and dy:
                new_y = self.rect.y + dy * self.rect.height * self.speed
                # Vérifier les limites de la carte
                if new_y < 0:
                    new_y = 0
                elif new_y > game.height * self.rect.height - self.rect.height:
                    new_y = game.height * self.rect.height - self.rect.height
            
            # Vérifier si le mouvement est possible (pas de collision)
            if not self.can_move(game=game, new_x=new_x, new_y=new_y):
                return  # Annuler le mouvement si collision
            
            # Déplacer l'unité
            self.rect.x = new_x
            self.rect.y = new_y
            
        
        
            
        
        
        
    
        
    


