import pygame
import time


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE SOLDAT : Classe de base pour toutes les unités du jeu
# Gère les stats, l'attaque, le déplacement et les collisions
# ═══════════════════════════════════════════════════════════════════════════════
class Soldat(pygame.sprite.Sprite):

    def __init__(self, x, y, img_path, owner: int = 0):
        super().__init__()
        
        if img_path:
            original_img = pygame.image.load(img_path)
            new_w = original_img.get_width() // 2
            new_h = original_img.get_height() // 2
            self.image = pygame.transform.scale(original_img, (new_w, new_h))
            self.rect = self.image.get_rect()
            self.rect.x = x * self.rect.width
            self.rect.y = y * self.rect.height
            self.exact_x = float(self.rect.x)
            self.exact_y = float(self.rect.y)
            
        self.is_alive = True
        self.team = owner
        self.last_attack_time = 0
        
    def update_animation(self):
        pass

    def __str__(self):
        return f"The {self.name} soldat have {self.hp}HP"


    # ═══════════════════════════════════════════════════════════════════════════════
    # SYSTÈME D'ATTAQUE : Calcule les dégâts en fonction de l'armure et des bonus
    # Gère le cooldown entre les attaques et la mort des unités
    # ═══════════════════════════════════════════════════════════════════════════════
    def attack(self, soldat, current_time=None):
        if current_time is None:
            current_time = time.time()
        
        if current_time - self.last_attack_time < self.reload_time:
            return
        
        self.last_attack_time = current_time
        
        armor = soldat.armor if self.is_close_combat else soldat.armor_pierce
        damage = self.damage
        if soldat.name in self.vs:
            damage = self.damage + self.vs[soldat.name]
        
        final_damage = max(1, damage - armor)
        soldat.hp -= final_damage
        
        if soldat.hp <= 0:
            soldat.is_alive = False
            soldat.kill()
            
        return None


    # ═══════════════════════════════════════════════════════════════════════════════
    # VÉRIFICATION DE MOUVEMENT : Détecte les collisions avec les autres unités
    # Permet de traverser les unités avec lesquelles on est déjà en collision
    # ═══════════════════════════════════════════════════════════════════════════════
    def can_move(self, game, new_x=None, new_y=None):
        future_rect = self.rect.copy()
        
        if new_x is not None:
            future_rect.x = new_x
        if new_y is not None:
            future_rect.y = new_y

        current_overlaps = []
        for soldat in game.all_soldats:
            if soldat is self: continue
            if self.rect.colliderect(soldat.rect):
                current_overlaps.append(soldat)
        
        for soldat in game.all_soldats:
            if soldat is self: continue
            if future_rect.colliderect(soldat.rect):
                if soldat not in current_overlaps:
                    return False
        
        return True


    # ═══════════════════════════════════════════════════════════════════════════════
    # DÉPLACEMENT : Gère le mouvement pixel par pixel avec gestion des limites
    # Tente un mouvement diagonal, sinon essaie X ou Y séparément
    # ═══════════════════════════════════════════════════════════════════════════════
    def move(self, game, dx=None, dy=None):
        with game.lock:
            new_x = self.exact_x
            new_y = self.exact_y
            
            map_limit_w = game.width * self.rect.width - self.rect.width
            map_limit_h = game.height * self.rect.height - self.rect.height

            if dx and dx != 0:
                new_x += dx * self.speed
                if new_x < 0: new_x = 0
                elif new_x > map_limit_w: new_x = map_limit_w
            
            if dy and dy != 0:
                new_y += dy * self.speed
                if new_y < 0: new_y = 0
                elif new_y > map_limit_h: new_y = map_limit_h
            
            if self.can_move(game=game, new_x=int(new_x), new_y=int(new_y)):
                self.exact_x = new_x
                self.exact_y = new_y
                self.rect.x = int(self.exact_x)
                self.rect.y = int(self.exact_y)
            else:
                if dx != 0 and dy != 0:
                    if self.can_move(game=game, new_x=int(new_x), new_y=self.rect.y):
                        self.exact_x = new_x
                        self.rect.x = int(self.exact_x)
                    elif self.can_move(game=game, new_x=self.rect.x, new_y=int(new_y)):
                        self.exact_y = new_y
                        self.rect.y = int(self.exact_y)

# ═══════════════════════════════════════════════════════════════════════════════
# ANIMATION : Met à jour la frame courante pour l'animation du Knight
# Cycle à travers les frames du spritesheet selon la vitesse définie
# ═══════════════════════════════════════════════════════════════════════════════
    def update_animation(self):
        if not self.frames:
            return
        
        self.animation_timer += 1
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]