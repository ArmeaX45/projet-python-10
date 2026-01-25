# src/ColonelSMART.py
# IA ULTRA-DOMINANTE V3 - STRATÉGIE DE VICTOIRE ABSOLUE
import math
import random


class ColonelSMART:
    """
    IA SUPRÊME - Conçue pour DOMINER et GAGNER à chaque fois.
    
    STRATÉGIE PRINCIPALE:
    1. Formation en "Mur de Fer" - Protection maximale des Arbalétriers
    2. Ciblage par CONTRE - Chaque unité chasse son contre
    3. Mouvement coordonné - Pas de files d'attente, tout le monde attaque
    4. Focus Fire - Concentrer les dégâts pour éliminer vite
    """
    
    # Qui chasse qui (rock-paper-scissors)
    HUNT_TARGET = {
        "Paladin": "Arbalester",      # Paladins chassent les Arbalétriers
        "Halberdier": "Paladin",      # Hallebardiers chassent les Paladins
        "Arbalester": "Halberdier",   # Arbalétriers chassent les Hallebardiers
    }
    
    # Qui fuir
    FLEE_FROM = {
        "Arbalester": "Paladin",      # Arbalétriers fuient les Paladins
        "Paladin": None,
        "Halberdier": None,
    }

    def __init__(self, team_name=0):
        self.team_name = team_name
        self.spread_direction = {}  # Mémorise la direction de décalage par unité

    @staticmethod
    def get_formation(team_id, width, height, config):
        """
        Formation en COLONNES ORGANISÉES - Simple et efficace.
        Identique à l'ancienne formation par défaut.
        
        [ARRIÈRE]  [MILIEU]  [FRONT]
           Arb       Pal      Halb
           Arb       Pal      Halb
           Arb       Pal      Halb
        """
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
        
        # ORDRE: Arbalester (fond) -> Paladin (milieu) -> Halberdier (front)
        unit_order = ["Arbalester", "Paladin", "Halberdier"]
        current_col = 0
        
        for unit_type in unit_order:
            count = config.get(unit_type, 0)
            if count <= 0:
                continue
            
            # Plus d'espacement pour élargir la formation
            x = start_x + (current_col * col_spacing * 1.5 * x_dir)
            
            # Centrage vertical
            total_height = (count - 1) * row_spacing
            start_y = center_y - total_height / 2
            
            for i in range(count):
                y = start_y + i * row_spacing
                # Utiliser toute la largeur disponible (plus d'espace sur les côtés)
                fx = max(0, min(width - 1, int(x)))
                fy = max(0, min(height - 1, int(y)))
                positions.append((unit_type, fx, fy))
            
            current_col += 1
        
        return positions

    def update(self, map_instance):
        """Mise à jour ultra-intelligente de toutes les unités."""
        actions = []
        
        allies = [u for u in map_instance.all_soldats if u.team == self.team_name and u.is_alive]
        enemies = [u for u in map_instance.all_soldats if u.team != self.team_name and u.is_alive]
        
        if not enemies:
            return actions
        
        # Pré-calcul: grouper les ennemis par type
        enemy_by_type = {
            "Arbalester": [e for e in enemies if e.name == "Arbalester"],
            "Paladin": [e for e in enemies if e.name == "Paladin"],
            "Halberdier": [e for e in enemies if e.name == "Halberdier"],
        }
        
        for unit in allies:
            tile = unit.rect.width
            # AUGMENTATION DE LA PORTÉE D'ATTAQUE
            attack_range = (unit.attack_range * tile) if unit.attack_range > 0 else tile * 1.6
            
            # === 1. KITING (Arbalétriers) ===
            if unit.name == "Arbalester":
                threat_type = self.FLEE_FROM.get(unit.name)
                if threat_type:
                    threats = enemy_by_type.get(threat_type, [])
                    if threats:
                        nearest_threat = min(threats, key=lambda t: self._dist(unit, t))
                        if self._dist(unit, nearest_threat) < tile * 5:
                            dx, dy = self._calculate_flee(unit, nearest_threat, allies, enemies, tile, map_instance)
                            if dx != 0 or dy != 0:
                                actions.append(("move", unit, dx, dy))
            
            # === 2. ATTAQUE - Priorité ABSOLUE si à portée ou collision ===
            # On vérifie d'abord si on touche quelqu'un (collision) -> Attaque immédiate pour éviter de vibrer
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
            
            # === 3. MOUVEMENT ===
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

    # ... (méthodes inchangées omises) ...

    def _can_move_to(self, unit, dx, dy, all_units, tile, map_inst):
        """Vérifie si le mouvement est possible."""
        if dx == 0 and dy == 0:
            return False
            
        fx = unit.rect.centerx + dx * tile * 0.8
        fy = unit.rect.centery + dy * tile * 0.8
        
        # Limites de la carte
        max_x = map_inst.width * tile
        max_y = map_inst.height * tile
        if fx < tile/2 or fx > max_x - tile/2 or fy < tile/2 or fy > max_y - tile/2:
            return False
        
        # Collision STRICTE avec autres unités (0.9 au lieu de 0.75)
        # Empêche la superposition
        for other in all_units:
            if other is unit:
                continue
            dist = math.hypot(other.rect.centerx - fx, other.rect.centery - fy)
            if dist < tile * 0.85: # Plus strict
                return False
        
        return True

    def _find_best_target(self, unit, enemies, enemy_by_type, attack_range):
        """Trouve la meilleure cible dans la portée d'attaque."""
        in_range = [e for e in enemies if self._dist(unit, e) <= attack_range]
        if not in_range:
            return None
        
        # Priorité 1: Cible de chasse (contre)
        hunt_type = self.HUNT_TARGET.get(unit.name)
        if hunt_type:
            counters_in_range = [e for e in in_range if e.name == hunt_type]
            if counters_in_range:
                # Focus fire: cibler celui avec le moins de HP
                return min(counters_in_range, key=lambda e: e.hp)
        
        # Priorité 2: Celui avec le moins de HP (focus fire)
        return min(in_range, key=lambda e: e.hp)

    def _calculate_flee(self, unit, threat, allies, enemies, tile, map_inst):
        """Calcule la direction de fuite intelligente."""
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = threat.rect.centerx, threat.rect.centery
        
        # Direction opposée à la menace
        flee_dx = 1 if ux > tx else -1 if ux < tx else 0
        flee_dy = 1 if uy > ty else -1 if uy < ty else 0
        
        all_units = allies + enemies
        
        # Essayer plusieurs directions de fuite
        directions = [
            (flee_dx, flee_dy),      # Fuite directe
            (flee_dx, 0),            # Horizontal
            (0, flee_dy),            # Vertical
            (flee_dx, -flee_dy),     # Diagonal alternatif
            (-flee_dx, flee_dy),     # Autre diagonal
        ]
        
        for dx, dy in directions:
            if dx == 0 and dy == 0:
                continue
            if self._can_move_to(unit, dx, dy, all_units, tile, map_inst):
                return dx, dy
        
        return 0, 0

    def _smart_pathfind(self, unit, target, allies, enemies, tile, map_inst):
        """Pathfinding intelligent avec décalage automatique."""
        unit_id = id(unit)
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = target.rect.centerx, target.rect.centery
        
        # Direction vers la cible
        want_dx = 1 if tx > ux + 3 else -1 if tx < ux - 3 else 0
        want_dy = 1 if ty > uy + 3 else -1 if ty < uy - 3 else 0
        
        if want_dx == 0 and want_dy == 0:
            return 0, 0
        
        all_units = allies + enemies
        
        # 1. Essayer mouvement direct
        if self._can_move_to(unit, want_dx, want_dy, all_units, tile, map_inst):
            self.spread_direction.pop(unit_id, None)
            return want_dx, want_dy
        
        # 2. DÉCALAGE INTELLIGENT si bloqué par un allié
        blocking_ally = self._get_blocking_ally(unit, want_dx, want_dy, allies, tile)
        
        if blocking_ally:
            # Choisir une direction de décalage cohérente
            if unit_id not in self.spread_direction:
                # Décider: haut ou bas / gauche ou droite
                if uy > ty:
                    self.spread_direction[unit_id] = -1  # Aller vers le haut
                else:
                    self.spread_direction[unit_id] = 1   # Aller vers le bas
            
            spread = self.spread_direction[unit_id]
            
            # Essayer de glisser latéralement tout en avançant
            spread_moves = [
                (want_dx, spread),      # Avancer + décaler
                (0, spread),            # Juste décaler
                (want_dx, -spread),     # Essayer l'autre côté
            ]
            
            for dx, dy in spread_moves:
                if self._can_move_to(unit, dx, dy, all_units, tile, map_inst):
                    return dx, dy
        
        # 3. Essayer toutes les directions
        all_dirs = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        # Trier par proximité avec la direction voulue
        all_dirs.sort(key=lambda d: -(d[0]*want_dx + d[1]*want_dy))
        
        for dx, dy in all_dirs:
            if self._can_move_to(unit, dx, dy, all_units, tile, map_inst):
                return dx, dy
        
        return 0, 0

    def _get_blocking_ally(self, unit, dx, dy, allies, tile):
        """Vérifie si un allié bloque le chemin."""
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
        """Vérifie si le mouvement est possible."""
        if dx == 0 and dy == 0:
            return False
            
        fx = unit.rect.centerx + dx * tile * 0.8
        fy = unit.rect.centery + dy * tile * 0.8
        
        # Limites de la carte
        max_x = map_inst.width * tile
        max_y = map_inst.height * tile
        if fx < tile/2 or fx > max_x - tile/2 or fy < tile/2 or fy > max_y - tile/2:
            return False
        
        # Collision avec autres unités
        for other in all_units:
            if other is unit:
                continue
            dist = math.hypot(other.rect.centerx - fx, other.rect.centery - fy)
            if dist < tile * 0.75:
                return False
        
        return True

    @staticmethod
    def _dist(a, b):
        """Distance entre deux unités."""
        return math.hypot(b.rect.centerx - a.rect.centerx, b.rect.centery - a.rect.centery)
