# Project: MedievAIl BAIttle GenerAIl
# IA "Braindead" : Défensive, ne bouge pas, attaque le plus proche

import math

class GeneralBrainDead:
    """IA défensive stupide : ne bouge JAMAIS, attaque juste l'ennemi le plus proche à portée."""
    
    def __init__(self, team_name=0):
        self.team_name = team_name

    def update(self, map_instance):
        """Ne bouge pas, attaque le plus proche si à portée."""
        actions = []

        allies = [u for u in map_instance.all_soldats if getattr(u, 'team', None) == self.team_name]
        enemies = [u for u in map_instance.all_soldats if getattr(u, 'team', None) != self.team_name]

        for unit in allies:
            if not enemies:
                continue
            
            tile = unit.rect.width
            # Augmenter la portée melee pour être sûr de toucher (couvre diagonales)
            attack_range = (unit.attack_range * tile) if unit.attack_range > 0 else tile * 1.6
            
            # Trouver l'ennemi le plus proche (peu importe le type)
            closest = min(enemies, key=lambda e: self._distance(unit, e))
            dist = self._distance(unit, closest)
            
            # Attaquer si à portée OU si on touche l'ennemi (collision)
            if dist <= attack_range or unit.rect.colliderect(closest.rect):
                actions.append(("attack", unit, closest))

        return actions
    
    @staticmethod
    def _distance(a, b):
        return math.hypot(b.rect.centerx - a.rect.centerx, b.rect.centery - a.rect.centery)


