# src/soldat.py
import pygame
import time

class Soldat(pygame.sprite.Sprite):

    def __init__(self, x, y, img_path, owner: int = 0):
        super().__init__()
        
        if img_path:
            original_img = pygame.image.load(img_path)
            # Réduire la taille des soldats (50% de l'original)
            new_w = original_img.get_width() // 2
            new_h = original_img.get_height() // 2
            self.image = pygame.transform.scale(original_img, (new_w, new_h))
            self.rect = self.image.get_rect()
            # Position initiale sur la grille (case * taille)
            self.rect.x = x * self.rect.width
            self.rect.y = y * self.rect.height
            
            # NOUVEAU: On stocke la position exacte en float pour la fluidité
            self.exact_x = float(self.rect.x)
            self.exact_y = float(self.rect.y)
            
        self.is_alive = True
        self.team = owner
        
        self.last_attack_time = 0   # Timestamp de la dernière attaque
        
    def update_animation(self):
        """Méthode d'animation (stub - peut être surchargée par les sous-classes)."""
        pass  # Par défaut, pas d'animation spéciale
        
    def __str__(self):
        return f"The {self.name} soldat have {self.hp}HP"
    
    def attack(self, soldat, current_time=None):
        
        if current_time is None:
            current_time = time.time()
        
        if current_time - self.last_attack_time < self.reload_time:
            return  # Not enough time has passed since the last attack
        
        self.last_attack_time = current_time # Update last attack time
        
        armor = soldat.armor if self.is_close_combat else soldat.armor_pierce
        damage = self.damage
        if soldat.name in self.vs:
            damage = self.damage + self.vs[soldat.name]
        
        final_damage = max(1, damage - armor)
        soldat.hp -= final_damage
        
        if soldat.hp <= 0:
            soldat.is_alive = False
            soldat.kill()  # Retire le sprite de tous les groupes pygame
            
        
        # print(f"{self.name} cause {damage} at {soldat.name}")
        
        return None
    
    def can_move(self, game, new_x=None, new_y=None):
        future_rect = self.rect.copy()
        
        if new_x is not None:
            future_rect.x = new_x
        if new_y is not None:
            future_rect.y = new_y

        # 1. Identifier les voisins avec qui on est DÉJÀ en collision (overlaps)
        current_overlaps = []
        for soldat in game.all_soldats:
            if soldat is self: continue
            if self.rect.colliderect(soldat.rect):
                current_overlaps.append(soldat)
        
        # 2. Vérifier collision FUTURE
        # Règle : On ne peut pas entrer dans une NOUVELLE unit.
        # Mais on a le droit de rester dans (ou traverser) celle qui nous bloque déjà (pour sortir).
        for soldat in game.all_soldats:
            if soldat is self: continue
            
            # Si on touche ce soldat dans le futur...
            if future_rect.colliderect(soldat.rect):
                # Est-ce un nouveau voisin ?
                if soldat not in current_overlaps:
                    return False # BLOQUÉ : on ne traverse pas les nouveaux
                
                # Si c'est un ancien voisin, c'est toléré (on essaie de sortir)
        
        return True

    def move(self, game, dx=None, dy=None):
        with game.lock:
            # On part de la position exacte actuelle
            new_x = self.exact_x
            new_y = self.exact_y
            
            # --- MODIFICATION MAJEURE ICI ---
            # Avant : new_x += dx * self.rect.width * self.speed (Saut d'une case entière)
            # Après : new_x += dx * self.speed (Déplacement de quelques pixels seulement)
            
            map_limit_w = game.width * self.rect.width - self.rect.width
            map_limit_h = game.height * self.rect.height - self.rect.height

            if dx and dx != 0:
                new_x += dx * self.speed
                # Limites de la carte
                if new_x < 0: new_x = 0
                elif new_x > map_limit_w: new_x = map_limit_w
            
            if dy and dy != 0:
                new_y += dy * self.speed
                # Limites de la carte
                if new_y < 0: new_y = 0
                elif new_y > map_limit_h: new_y = map_limit_h
            
            # On vérifie si on peut bouger en convertissant en int pour le Rect
            if self.can_move(game=game, new_x=int(new_x), new_y=int(new_y)):
                # Si c'est bon, on met à jour les coordonnées précises et le Rect
                self.exact_x = new_x
                self.exact_y = new_y
                self.rect.x = int(self.exact_x)
                self.rect.y = int(self.exact_y)
            else:
                # Si on ne peut pas bouger en diagonale, on essaie juste X ou juste Y
                if dx != 0 and dy != 0:
                     # Essaie juste X
                    if self.can_move(game=game, new_x=int(new_x), new_y=self.rect.y):
                        self.exact_x = new_x
                        self.rect.x = int(self.exact_x)
                    # Sinon essaie juste Y
                    elif self.can_move(game=game, new_x=self.rect.x, new_y=int(new_y)):
                        self.exact_y = new_y
                        self.rect.y = int(self.exact_y)