# src/ai_braindead.py
# IA défensive : fait avancer les soldats puis attaque
import math


class CaptainBraindead:
    """IA simple défensive : avance les soldats vers le centre, attaque à portée."""
    
    def __init__(self, team_name=0):
        self.team_name = team_name

    def update(self, map_instance):
        """Fait avancer les soldats et attaque si ennemi à portée."""
        actions = []

        allies = [u for u in map_instance.all_soldats if getattr(u, "team", None) == self.team_name]
        enemies = [u for u in map_instance.all_soldats if getattr(u, "team", None) != self.team_name]

        for unit in allies:
            if not enemies:
                continue

            tile = unit.rect.width
            range_px = (unit.attack_range * tile) if unit.attack_range > 0 else tile * 1.3

            # Chercher ennemi à portée
            target_in_range = None
            for e in enemies:
                if self._distance(unit, e) <= range_px:
                    target_in_range = e
                    break

            if target_in_range:
                # Attaquer
                actions.append(("attack", unit, target_in_range))
            else:
                # Avancer vers l'ennemi le plus proche
                target = self._nearest_enemy(unit, enemies)
                if target:
                    dx, dy = self._get_direction(unit, target)
                    actions.append(("move", unit, dx, dy))

        return actions

    def _get_direction(self, unit, target):
        """Direction simple vers la cible."""
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = target.rect.centerx, target.rect.centery

        dx = 1 if tx > ux + 5 else -1 if tx < ux - 5 else 0
        dy = 1 if ty > uy + 5 else -1 if ty < uy - 5 else 0

        if abs(tx - ux) > abs(ty - uy):
            return dx, 0
        return 0, dy

    def _nearest_enemy(self, unit, enemies):
        best = None
        best_d = float("inf")
        for e in enemies:
            d = self._distance(unit, e)
            if d < best_d:
                best_d = d
                best = e
        return best

    @staticmethod
    def _distance(a, b):
        return math.hypot(b.rect.centerx - a.rect.centerx, b.rect.centery - a.rect.centery)
