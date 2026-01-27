import math
import random


# ═══════════════════════════════════════════════════════════════════════════════
# IA COLONELSMART : Intelligence artificielle avancée avec stratégie tactique
# Utilise le système pierre-feuille-ciseaux : chaque unité chasse son contre
# ═══════════════════════════════════════════════════════════════════════════════
class ColonelSMART:
    
    HUNT_TARGET = {
        "Paladin": "Arbalester",
        "Halberdier": "Paladin",
        "Arbalester": "Halberdier",
    }
    
    fuit_qui = {
        "Arbalester": "Paladin",
        "Paladin": None,
        "Halberdier": None,
    }

    def __init__(self, team_name=0):
        self.team_name = team_name
        self.spread_direction = {}


    # ═══════════════════════════════════════════════════════════════════════════════
    # FORMATION : Placement en colonnes organisées avec ordre tactique
    # Arbalétriers à l'arrière, Paladins au milieu, Hallebardiers en front
    # ═══════════════════════════════════════════════════════════════════════════════
    @staticmethod
    def get_formation(team_id, width, height, config):
        positions = []
        
        if team_id == 0:
            start_x = 2
            x_dir = 1
        else:
            start_x = width - 3
            x_dir = -1
        
        col_spacing = 2
        row_spacing = 1.3
        center_y = height / 2
        
        unit_order = ["Arbalester", "Paladin", "Halberdier"]
        current_col = 0
        
        for unit_type in unit_order:
            count = config.get(unit_type, 0)
            if count <= 0:
                continue
            
            x = start_x + (current_col * col_spacing * 1.5 * x_dir)
            
            total_height = (count - 1) * row_spacing
            start_y = center_y - total_height / 2
            
            for i in range(count):
                y = start_y + i * row_spacing
                fx = max(0, min(width - 1, int(x)))
                fy = max(0, min(height - 1, int(y)))
                positions.append((unit_type, fx, fy))
            
            current_col += 1
        
        return positions


    # ═══════════════════════════════════════════════════════════════════════════════
    # MISE À JOUR : Boucle principale avec kiting, attaque prioritaire et mouvement
    # Gère la fuite des Arbalétriers, le focus fire et le pathfinding intelligent
    # ═══════════════════════════════════════════════════════════════════════════════
    def update(self, map_instance):
        actions = []
        
        allies = [u for u in map_instance.all_soldats if u.team == self.team_name and u.is_alive]
        enemies = [u for u in map_instance.all_soldats if u.team != self.team_name and u.is_alive]
        
        if not enemies:
            return actions
        
        enemy_by_type = {
            "Arbalester": [e for e in enemies if e.name == "Arbalester"],
            "Paladin": [e for e in enemies if e.name == "Paladin"],
            "Halberdier": [e for e in enemies if e.name == "Halberdier"],
        }
        
        for unit in allies:
            tile = unit.rect.width
            attack_range = (unit.attack_range * tile) if unit.attack_range > 0 else tile * 1.6
            
            if unit.name == "Arbalester":
                threat_type = self.fuit_qui.get(unit.name)
                if threat_type:
                    threats = enemy_by_type.get(threat_type, [])
                    if threats:
                        nearest_threat = min(threats, key=lambda t: self._dist(unit, t))
                        if self._dist(unit, nearest_threat) < tile * 3.5:
                            dx, dy = self._calculate_flee(unit, nearest_threat, allies, enemies, tile, map_instance)
                            if dx != 0 or dy != 0:
                                actions.append(("move", unit, dx, dy))
            
            colliding_enemy = None
            for enemy in enemies:
                if unit.rect.colliderect(enemy.rect):
                    colliding_enemy = enemy
                    break
            
            if colliding_enemy:
                actions.append(("attack", unit, colliding_enemy))
                continue

            target = self._find_best_target(unit, enemies, enemy_by_type, attack_range)
            if target:
                actions.append(("attack", unit, target))
                continue
            
            hunt_type = self.HUNT_TARGET.get(unit.name)
            move_target = None
            
            if hunt_type:
                candidates = enemy_by_type.get(hunt_type, [])
                if candidates:
                    move_target = min(candidates, key=lambda e: self._dist(unit, e))
            
            if not move_target:
                 move_target = min(enemies, key=lambda e: self._dist(unit, e))
            
            if move_target:
                dx, dy = self._smart_pathfind(unit, move_target, allies, enemies, tile, map_instance)
                if dx != 0 or dy != 0:
                    actions.append(("move", unit, dx, dy))
        
        return actions


    # ═══════════════════════════════════════════════════════════════════════════════
    # SÉLECTION DE CIBLE : Trouve la meilleure cible à portée avec priorité au contre
    # Applique le focus fire en ciblant l'unité avec le moins de PV
    # ═══════════════════════════════════════════════════════════════════════════════
    def _find_best_target(self, unit, enemies, enemy_by_type, attack_range):
        in_range = [e for e in enemies if self._dist(unit, e) <= attack_range]
        if not in_range:
            return None
        
        hunt_type = self.HUNT_TARGET.get(unit.name)
        if hunt_type:
            counters_in_range = [e for e in in_range if e.name == hunt_type]
            if counters_in_range:
                return min(counters_in_range, key=lambda e: e.hp)
        
        return min(in_range, key=lambda e: e.hp)


    # ═══════════════════════════════════════════════════════════════════════════════
    # FUITE INTELLIGENTE : Calcule la direction de fuite pour les Arbalétriers
    # Essaie plusieurs directions de fuite si la principale est bloquée
    # ═══════════════════════════════════════════════════════════════════════════════
    def _calculate_flee(self, unit, threat, allies, enemies, tile, map_inst):
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = threat.rect.centerx, threat.rect.centery
        
        flee_dx = 1 if ux > tx else -1 if ux < tx else 0
        flee_dy = 1 if uy > ty else -1 if uy < ty else 0
        
        all_units = allies + enemies
        
        directions = [
            (flee_dx, flee_dy),
            (flee_dx, 0),
            (0, flee_dy),
            (flee_dx, -flee_dy),
            (-flee_dx, flee_dy),
        ]
        
        for dx, dy in directions:
            if dx == 0 and dy == 0:
                continue
            if self._can_move_to(unit, dx, dy, all_units, tile, map_inst):
                return dx, dy
        
        return 0, 0


    # ═══════════════════════════════════════════════════════════════════════════════
    # PATHFINDING INTELLIGENT : Mouvement vers la cible avec décalage automatique
    # Gère le contournement des alliés bloquants et essaie plusieurs directions
    # ═══════════════════════════════════════════════════════════════════════════════
    def _smart_pathfind(self, unit, target, allies, enemies, tile, map_inst):
        unit_id = id(unit)
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = target.rect.centerx, target.rect.centery
        
        want_dx = 1 if tx > ux + 3 else -1 if tx < ux - 3 else 0
        want_dy = 1 if ty > uy + 3 else -1 if ty < uy - 3 else 0
        
        if want_dx == 0 and want_dy == 0:
            return 0, 0
        
        all_units = allies + enemies
        
        if self._can_move_to(unit, want_dx, want_dy, all_units, tile, map_inst):
            self.spread_direction.pop(unit_id, None)
            return want_dx, want_dy
        
        blocking_ally = self._get_blocking_ally(unit, want_dx, want_dy, allies, tile)
        
        if blocking_ally:
            if unit_id not in self.spread_direction:
                if uy > ty:
                    self.spread_direction[unit_id] = -1
                else:
                    self.spread_direction[unit_id] = 1
            
            spread = self.spread_direction[unit_id]
            
            spread_moves = [
                (want_dx, spread),
                (0, spread),
                (want_dx, -spread),
            ]
            
            for dx, dy in spread_moves:
                if self._can_move_to(unit, dx, dy, all_units, tile, map_inst):
                    return dx, dy
        
        all_dirs = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        all_dirs.sort(key=lambda d: -(d[0]*want_dx + d[1]*want_dy))
        
        for dx, dy in all_dirs:
            if self._can_move_to(unit, dx, dy, all_units, tile, map_inst):
                return dx, dy
        
        return 0, 0

    def _get_blocking_ally(self, unit, dx, dy, allies, tile):
        fx = unit.rect.centerx + dx * tile
        fy = unit.rect.centery + dy * tile
        
        for ally in allies:
            if ally is unit:
                continue
            dist = math.hypot(ally.rect.centerx - fx, ally.rect.centery - fy)
            if dist < tile * 0.9:
                return ally
        return None

    def _can_move_to(self, unit, dx, dy, all_units, tile, map_inst):
        if dx == 0 and dy == 0:
            return False
            
        fx = unit.rect.centerx + dx * tile * 0.8
        fy = unit.rect.centery + dy * tile * 0.8
        
        max_x = map_inst.width * tile
        max_y = map_inst.height * tile
        if fx < tile/2 or fx > max_x - tile/2 or fy < tile/2 or fy > max_y - tile/2:
            return False
        
        for other in all_units:
            if other is unit:
                continue
            dist = math.hypot(other.rect.centerx - fx, other.rect.centery - fy)
            if dist < tile * 0.75:
                return False
        
        return True

    @staticmethod
    def _dist(a, b):
        return math.hypot(b.rect.centerx - a.rect.centerx, b.rect.centery - a.rect.centery)
