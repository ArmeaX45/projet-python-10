# src/ColonelSMART.py
# IA ÉLITE - Formation optimale + ciblage avec priorités ABSOLUES
import math
import random


class ColonelSMART:
    """IA élite avec formation et priorités absolues de ciblage."""
    
    # PRIORITÉS ABSOLUES : si la cible prioritaire existe, on l'attaque en premier
    # Paladin -> DOIT cibler Arbalester (les tue facilement)
    # Halberdier -> DOIT cibler Paladin (bonus +22 dégâts)
    # Arbalester -> DOIT cibler Halberdier (bonus +3, distance de sécurité)
    ABSOLUTE_PRIORITY = {
        "Paladin": "Arbalester",     # Paladin chasse les archers
        "Halberdier": "Paladin",     # Halberdier contre cavalerie
        "Arbalester": "Halberdier",  # Arbalétrier cible infanterie
    }

    def __init__(self, team_name=0):
        self.team_name = team_name
        self.bypass_direction = {}
        self.assigned_targets = {}

    @staticmethod
    def get_formation(team_id, width, height, config):
        """Formation en V : Paladins devant, Halberdiers flancs, Arbalétriers arrière."""
        positions = []
        center_y = height // 2
        
        if team_id == 0:
            # Équipe gauche
            front_x = 3
            
            # Paladins en pointe de V
            paladin_count = config.get("Paladin", 0)
            for i in range(paladin_count):
                row = i // 2
                offset = ((i % 2) * 2 - 1) * (row + 1) if i > 0 else 0
                positions.append(("Paladin", front_x + row, center_y + offset))
            
            # Halberdiers sur les flancs
            halberdier_count = config.get("Halberdier", 0)
            for i in range(halberdier_count):
                side = 1 if i % 2 == 0 else -1
                offset = (i // 2 + 2) * 2
                positions.append(("Halberdier", front_x + 1, center_y + side * offset))
            
            # Arbalétriers en ligne arrière espacés
            arbalester_count = config.get("Arbalester", 0)
            if arbalester_count > 0:
                spacing = max(2, (height - 4) // arbalester_count)
                for i in range(arbalester_count):
                    positions.append(("Arbalester", 1, 2 + i * spacing))
        else:
            # Équipe droite (miroir)
            front_x = width - 4
            
            paladin_count = config.get("Paladin", 0)
            for i in range(paladin_count):
                row = i // 2
                offset = ((i % 2) * 2 - 1) * (row + 1) if i > 0 else 0
                positions.append(("Paladin", front_x - row, center_y + offset))
            
            halberdier_count = config.get("Halberdier", 0)
            for i in range(halberdier_count):
                side = 1 if i % 2 == 0 else -1
                offset = (i // 2 + 2) * 2
                positions.append(("Halberdier", front_x - 1, center_y + side * offset))
            
            arbalester_count = config.get("Arbalester", 0)
            if arbalester_count > 0:
                spacing = max(2, (height - 4) // arbalester_count)
                for i in range(arbalester_count):
                    positions.append(("Arbalester", width - 2, 2 + i * spacing))
        
        return positions

    def update(self, map_instance):
        """IA avec priorités absolues."""
        actions = []
        self.assigned_targets = {}

        allies = [u for u in map_instance.all_soldats if getattr(u, "team", None) == self.team_name]
        enemies = [u for u in map_instance.all_soldats if getattr(u, "team", None) != self.team_name]

        if not enemies:
            return actions

        # Trier : arbalétriers d'abord (tirent à distance)
        sorted_allies = sorted(allies, key=lambda u: (0 if u.name == "Arbalester" else 1))

        for unit in sorted_allies:
            unit_id = id(unit)
            tile = unit.rect.width
            range_px = (unit.attack_range * tile) if unit.attack_range > 0 else tile * 1.5

            # === CIBLAGE AVEC PRIORITÉ ABSOLUE ===
            target = self._find_priority_target(unit, enemies, range_px)
            
            if target:
                actions.append(("attack", unit, target))
                self.assigned_targets[id(target)] = self.assigned_targets.get(id(target), 0) + 1
                if unit_id in self.bypass_direction:
                    del self.bypass_direction[unit_id]
                continue

            # Pas de cible à portée -> avancer vers la cible prioritaire
            move_target = self._find_priority_target_global(unit, enemies)
            if move_target:
                dx, dy = self._smart_move(unit, move_target, allies + enemies, tile)
                if dx != 0 or dy != 0:
                    actions.append(("move", unit, dx, dy))

        return actions

    def _find_priority_target(self, unit, enemies, range_px):
        """Trouve la cible à portée avec PRIORITÉ ABSOLUE."""
        unit_type = unit.name
        priority_type = self.ABSOLUTE_PRIORITY.get(unit_type)
        
        # D'abord chercher la cible prioritaire à portée
        if priority_type:
            for enemy in enemies:
                if enemy.name == priority_type and self._distance(unit, enemy) <= range_px:
                    return enemy
        
        # Ensuite, n'importe quelle cible à portée (préférer les blessés)
        best = None
        best_score = -1
        for enemy in enemies:
            if self._distance(unit, enemy) > range_px:
                continue
            hp_ratio = enemy.hp / enemy.max_hp
            score = (1 - hp_ratio) * 100 - self.assigned_targets.get(id(enemy), 0) * 30
            if score > best_score:
                best_score = score
                best = enemy
        
        return best

    def _find_priority_target_global(self, unit, enemies):
        """Trouve la cible prioritaire vers laquelle avancer."""
        unit_type = unit.name
        priority_type = self.ABSOLUTE_PRIORITY.get(unit_type)
        
        # Chercher d'abord la cible prioritaire
        if priority_type:
            priority_targets = [e for e in enemies if e.name == priority_type]
            if priority_targets:
                return min(priority_targets, key=lambda e: self._distance(unit, e))
        
        # Sinon, ennemi le plus proche
        return min(enemies, key=lambda e: self._distance(unit, e), default=None)

    def _smart_move(self, unit, target, all_units, tile):
        """Mouvement intelligent avec contournement."""
        unit_id = id(unit)
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = target.rect.centerx, target.rect.centery

        dx = 1 if tx > ux + 5 else -1 if tx < ux - 5 else 0
        dy = 1 if ty > uy + 5 else -1 if ty < uy - 5 else 0

        if self._blocked(unit, dx, dy, all_units, tile):
            if unit_id not in self.bypass_direction:
                self.bypass_direction[unit_id] = random.choice([-1, 1])
            bypass = self.bypass_direction[unit_id]
            
            if abs(tx - ux) > abs(ty - uy):
                if not self._blocked(unit, dx, bypass, all_units, tile):
                    return dx, bypass
                return 0, bypass
            else:
                if not self._blocked(unit, bypass, dy, all_units, tile):
                    return bypass, dy
                return bypass, 0
        else:
            if unit_id in self.bypass_direction:
                del self.bypass_direction[unit_id]
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

    @staticmethod
    def _distance(a, b):
        return math.hypot(b.rect.centerx - a.rect.centerx, b.rect.centery - a.rect.centery)
