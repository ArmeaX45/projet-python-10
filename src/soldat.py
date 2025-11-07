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

        self.is_alive = True
        self.owner = owner          # <-- AJOUT: 0 ou 1
        # garde tes attributs spécifiques dans les sous-classes
        # ex: vision_range, attack_range, speed, reload_time...

    def __str__(self):
        return f"The {self.name} soldat have {self.hp}HP"

    def attack(self, soldat):
        armor = soldat.armor if self.is_close_combat else soldat.armor_pierce
        damage = self.damage
        if soldat.name in self.vs:
            damage = self.damage + self.vs[soldat.name]
        soldat.hp -= max(0, (damage - armor))
        if soldat.hp <= 0:
            soldat.is_alive = False
        print(f"{self.name} cause {damage} at {soldat.name}")

    # --- Helpers de déplacement en tuiles ---
    def tile_pos(self):
        tw, th = self.rect.width, self.rect.height
        return (self.rect.x // tw, self.rect.y // th)

    def move_towards_tile(self, tx: int, ty: int):
        """Déplacement naïf d'une tuile par 'tick' vers (tx, ty) — à remplacer par ton pathfinding.
        Ici on fait juste un pas de 1 tuile en horizontal/vertical si nécessaire."""
        if not self.is_alive:
            return
        x, y = self.tile_pos()
        if (x, y) == (tx, ty):
            return
        nx, ny = x, y
        if tx > x: nx += 1
        elif tx < x: nx -= 1
        elif ty > y: ny += 1
        elif ty < y: ny -= 1
        # applique sur rect en pixels
        self.rect.x = nx * self.rect.width
        self.rect.y = ny * self.rect.height

    def can_attack(self, other: "Soldat") -> bool:
        if not other or not other.is_alive:
            return False
        x, y = self.tile_pos()
        ox, oy = other.tile_pos()
        dx, dy = x - ox, y - oy
        return (dx*dx + dy*dy) <= (max(0, self.attack_range) ** 2)

        
    
        
    


