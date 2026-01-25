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
        Formation SIMPLE BLOC - Pour éviter tout bug de placement.
        Les soldats sont regroupés en un carré au fond.
        """
        positions = []
        center_y = height / 2
        
        if team_id == 0:
            start_x = 2
            x_dir = 1
        else:
            start_x = width - 4
            x_dir = -1
            
        current_x = start_x
        current_y = 2
        
        all_units = []
        for unit_type, count in config.items():
            all_units.extend([unit_type] * count)
        random.shuffle(all_units) # Mélange mais placement propre
        
        # Placement en grille simple
        for unit_type in all_units:
            positions.append((unit_type, current_x, current_y))
            
            # Avancer en Y
            current_y += 1.5
            if current_y > height - 3:
                current_y = 2
                current_x += x_dir * 1.5 # Reculer d'une colonne
                
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