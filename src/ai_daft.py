# src/ai_daft.py
# IA offensive simple : avance directement vers l'ennemi et attaque
import math
import random


class MajorDaftSimple:
    """IA simple : avance tout droit vers l'ennemi, attaque à portée."""
    
    def __init__(self, team_name="A"):
        self.team_name = team_name
        self.bypass_direction = {}

    @staticmethod
    def get_formation(team_id, width, height, config):
        """
        Formation MAUVAISE - Soldats dispersés au hasard.
        Pas de stratégie, juste du chaos.
        """
        positions = []
        
        # Zone de spawn (1/4 de la map du côté de l'équipe)
        if team_id == 0:
            x_min, x_max = 1, width // 4
        else:
            x_min, x_max = width * 3 // 4, width - 2
        
        y_min, y_max = 2, height - 2
        occupied = set()
        
        # Spawn dans un ordre aléatoire (pas optimisé du tout)
        all_units = []
        for unit_type, count in config.items():
            all_units.extend([unit_type] * count)
        random.shuffle(all_units)  # Ordre aléatoire = mauvais
        
        for unit_type in all_units:
            # Position aléatoire
            for _ in range(50):  # Max 50 tentatives
                px = random.randint(x_min, x_max)
                py = random.randint(y_min, y_max)
                if (px, py) not in occupied:
                    occupied.add((px, py))
                    positions.append((unit_type, px, py))
                    break
        
        return positions

    def update(self, map_instance):
        """Renvoie des actions (attack / move)."""
        actions = []

        allies = [u for u in map_instance.all_soldats if getattr(u, "team", None) == self.team_name]
        enemies = [u for u in map_instance.all_soldats if getattr(u, "team", None) != self.team_name]

        for unit in allies:
            if not enemies:
                continue

            unit_id = id(unit)
            target = self._nearest_enemy(unit, enemies)
            if target is None:
                continue

            dist = self._distance(unit, target)
            tile = unit.rect.width
            range_px = (unit.attack_range * tile) if unit.attack_range > 0 else tile * 1.3

            # À portée -> attaquer
            if dist <= range_px:
                actions.append(("attack", unit, target))
                if unit_id in self.bypass_direction:
                    del self.bypass_direction[unit_id]
                continue

            # Sinon avancer
            dx, dy = self._get_direction(unit, target, allies + enemies, tile)
            if dx != 0 or dy != 0:
                actions.append(("move", unit, dx, dy))

        return actions

    def _get_direction(self, unit, target, all_units, tile):
        """Direction vers la cible avec contournement basique."""
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = target.rect.centerx, target.rect.centery

        dx = 1 if tx > ux + 5 else -1 if tx < ux - 5 else 0
        dy = 1 if ty > uy + 5 else -1 if ty < uy - 5 else 0

        # Vérifier blocage
        if self._blocked(unit, dx, dy, all_units, tile):
            unit_id = id(unit)
            if unit_id not in self.bypass_direction:
                self.bypass_direction[unit_id] = 1 if ty > uy else -1
            bypass = self.bypass_direction[unit_id]
            
            if abs(tx - ux) > abs(ty - uy):
                return dx, bypass
            else:
                return bypass, dy
        
        if abs(tx - ux) > abs(ty - uy):
            return dx, 0
        return 0, dy

    def _blocked(self, unit, dx, dy, all_units, tile):
        if dx == 0 and dy == 0:
            return False
        cx = unit.rect.centerx + dx * tile * 0.5
        cy = unit.rect.centery + dy * tile * 0.5
        for other in all_units:
            if other is unit:
                continue
            if abs(other.rect.centerx - cx) < tile * 0.7 and abs(other.rect.centery - cy) < tile * 0.7:
                return True
        return False

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