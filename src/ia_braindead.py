import math


# ═══════════════════════════════════════════════════════════════════════════════
# IA BRAINDEAD : Intelligence artificielle défensive passive
# Ne bouge jamais, attaque uniquement l'ennemi le plus proche à portée
# ═══════════════════════════════════════════════════════════════════════════════
class GeneralBrainDead:
    
    def __init__(self, team_name=0):
        self.team_name = team_name


    # ═══════════════════════════════════════════════════════════════════════════════
    # MISE À JOUR : Boucle de décision - reste immobile et attaque si possible
    # Vérifie la portée d'attaque ou la collision pour déclencher l'attaque
    # ═══════════════════════════════════════════════════════════════════════════════
    def update(self, map_instance):
        actions = []

        allies = [u for u in map_instance.all_soldats if getattr(u, 'team', None) == self.team_name]
        enemies = [u for u in map_instance.all_soldats if getattr(u, 'team', None) != self.team_name]

        for unit in allies:
            if not enemies:
                continue
            
            tile = unit.rect.width
            attack_range = (unit.attack_range * tile) if unit.attack_range > 0 else tile * 1.6
            
            closest = min(enemies, key=lambda e: self._distance(unit, e))
            dist = self._distance(unit, closest)
            
            if dist <= attack_range or unit.rect.colliderect(closest.rect):
                actions.append(("attack", unit, closest))

        return actions
    
    @staticmethod
    def _distance(a, b):
        return math.hypot(b.rect.centerx - a.rect.centerx, b.rect.centery - a.rect.centery)
