# src/ColonelSMART.py
# IA SUPREME : CONCAVE FORMATION + KITING + FLANKING
import math
import random


class ColonelSMART:
    """
    IA ULTRA-COMPETITIVE :
    1. Formation Arc (Concave) pour maximiser la surface de tir/contact.
    2. Kiting pour les Arbalétriers (reculent si menacés).
    3. Flanking pour les Paladins.
    4. Focus Fire mathématique.
    """
    
    TARGET_PRIORITY = {
        "Paladin": ["Arbalester", "Paladin", "Halberdier"],
        "Halberdier": ["Paladin", "Halberdier", "Arbalester"],
        "Arbalester": ["Halberdier", "Arbalester", "Paladin"],
    }

    def __init__(self, team_name=0):
        self.team_name = team_name
        self.path_memory = {}
        self.kite_cooldown = {} # Pour éviter d'hésiter entre avancer/reculer

    @staticmethod
    def get_formation(team_id, width, height, config):
        """
        Formation 'PHALANX' (Cubique/Lignes) :
        - Organisation stricte en lignes verticales pour un impact maximal de front.
        - Arbalester en arrière, Paladins au milieu/flancs, Halberdiers devant.
        """
        positions = []
        center_y = height / 2
        forward = 1 if team_id == 0 else -1
        base_x = 5 if team_id == 0 else width - 6
        
        def place_block(unit_type, count, start_x_offset, spacing_y=1.5):
            if count <= 0: return
            
            # Placement en bloc compact (colonne par colonne)
            # On remplit la hauteur diponible, puis on passe à la colonne suivante (vers l'arrière)
            available_h = height - 4
            max_per_col = int(available_h // spacing_y)
            if max_per_col < 1: max_per_col = 1
            
            items_placed = 0
            col = 0
            
            while items_placed < count:
                n_curr = min(count - items_placed, max_per_col)
                
                # Coordonnée X de la colonne (on recule pour chaque nouvelle colonne)
                # start_x_offset est le "front" du bloc
                x = base_x + ((start_x_offset - col * 2) * forward)
                
                # Centrage Y
                block_h = (n_curr - 1) * spacing_y
                start_y = center_y - block_h / 2
                
                for i in range(n_curr):
                    y = start_y + i * spacing_y
                    
                    # Clamp
                    fx = max(2, min(width - 3, int(x)))
                    fy = max(2, min(height - 2, int(y)))
                    
                    positions.append((unit_type, fx, fy))
                
                items_placed += n_curr
                col += 1

        # 1. HALBERDIERS (Frontline Stricte)
        # Mur devant
        hal_count = config.get("Halberdier", 0)
        place_block("Halberdier", hal_count, start_x_offset=10)

        # 2. PALADINS (Seconde Ligne / Flancs compacts)
        # Juste derrière les hallebardiers
        pal_count = config.get("Paladin", 0)
        place_block("Paladin", pal_count, start_x_offset=8)

        # 3. ARBALESTERS (Arrière Garde)
        # Bloc derrière
        arb_count = config.get("Arbalester", 0)
        place_block("Arbalester", arb_count, start_x_offset=4)
        
        return positions

    def update(self, map_instance):
        actions = []
        allies = [u for u in map_instance.all_soldats if getattr(u, "team", None) == self.team_name]
        enemies = [u for u in map_instance.all_soldats if getattr(u, "team", None) != self.team_name]

        if not enemies:
            return actions

        for unit in allies:
            # Stats
            tile = unit.rect.width
            # Sécurité
            safe_dist = tile * 4.0 if unit.name == "Arbalester" else tile * 2.0
            attack_range = (unit.attack_range * tile) if getattr(unit, "attack_range", 0) > 0 else tile * 1.2
            
            # Plus proche ennemi
            nearest_enemy = min(enemies, key=lambda e: self._distance(unit, e))
            dist_nearest = self._distance(unit, nearest_enemy)

            # === 1. KITING (Pour Arbalester) ===
            if unit.name == "Arbalester":
                # On ne fuit PAS les autres Arbalesters (duel de tir)
                if nearest_enemy.name != "Arbalester" and dist_nearest < safe_dist:
                    dx, dy = self._flee(unit, nearest_enemy, allies + enemies, tile, map_instance.width, map_instance.height)
                    if dx != 0 or dy != 0:
                        actions.append(("move", unit, dx, dy))
                        # Pas de continue ici ! On veut pouvoir tirer en reculant (Hit & Run)

            # === 2. ATTAQUE ===
            target = self._get_smart_target(unit, enemies, attack_range)
            
            # --- SPECIAL HALBERDIER FOCUS ---
            # Si on est un Hallebardier et qu'on vise autre chose qu'un Paladin...
            if unit.name == "Halberdier" and target and target.name != "Paladin":
                # Vérifier s'il reste des Paladins en vie sur la map
                paladins_alive = any(e.name == "Paladin" for e in enemies)
                if paladins_alive:
                    # OUI -> On IGNORE la cible actuelle (ex: un autre Hallebardier)
                    # Pour forcer le mouvement vers le Paladin (via Move Tactic plus bas)
                    target = None

            if target:
                actions.append(("attack", unit, target))
                if id(unit) in self.path_memory: del self.path_memory[id(unit)]
                continue

            # === 3. MOUVEMENT TACTIQUE ===
            move_target = self._get_strategic_target(unit, enemies)
            if move_target:
                dx, dy = self._smart_move(unit, move_target, allies + enemies, tile)
                if dx != 0 or dy != 0:
                    actions.append(("move", unit, dx, dy))
                else:
                    # SI BLOQUÉ : on essaie de bouger un peu au hasard pour se débloquer (Wiggle)
                    # Cela évite les embouteillages statiques
                    wiggle = self._wiggle(unit, allies + enemies, tile)
                    if wiggle:
                        actions.append(("move", unit, wiggle[0], wiggle[1]))

        return actions

    def _get_smart_target(self, unit, enemies, range_px):
        candidates = [e for e in enemies if self._distance(unit, e) <= range_px]
        if not candidates: return None
        priorities = self.TARGET_PRIORITY.get(unit.name, [])
        candidates.sort(key=lambda e: (priorities.index(e.name) if e.name in priorities else 99, e.hp, self._distance(unit, e)))
        return candidates[0]

    def _get_strategic_target(self, unit, enemies):
        priorities = self.TARGET_PRIORITY.get(unit.name, [])
        for p_name in priorities:
            targets = [e for e in enemies if e.name == p_name]
            if targets: return min(targets, key=lambda e: self._distance(unit, e))
        return min(enemies, key=lambda e: self._distance(unit, e))

    def _flee(self, unit, threat, obstacles, tile, map_w, map_h):
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = threat.rect.centerx, threat.rect.centery
        dx = 1 if ux > tx else -1 if ux < tx else 0
        dy = 1 if uy > ty else -1 if uy < ty else 0
        
        # Test 1 : Fuite directe
        if not self._is_blocked_prediction(unit, dx, dy, obstacles, tile, map_w, map_h):
            return dx, dy
            
        # Test 2 : Glissement (X ou Y seulement)
        if dx != 0 and not self._is_blocked_prediction(unit, dx, 0, obstacles, tile, map_w, map_h): return dx, 0
        if dy != 0 and not self._is_blocked_prediction(unit, 0, dy, obstacles, tile, map_w, map_h): return 0, dy
        
        return 0, 0

    def _smart_move(self, unit, target, obstacles, tile):
        unit_id = id(unit)
        ux, uy = unit.rect.centerx, unit.rect.centery
        tx, ty = target.rect.centerx, target.rect.centery
        
        dx = 1 if tx > ux + 5 else -1 if tx < ux - 5 else 0
        dy = 1 if ty > uy + 5 else -1 if ty < uy - 5 else 0
        
        if dx == 0 and dy == 0: return 0, 0

        # Mouvement direct libre ?
        if not self._is_blocked(unit, dx, dy, obstacles, tile):
            if unit_id in self.path_memory: del self.path_memory[unit_id]
            return dx, dy
            
        # Contournement mémorisé ?
        if unit_id in self.path_memory:
            pdx, pdy = self.path_memory[unit_id]
            if not self._is_blocked(unit, pdx, pdy, obstacles, tile):
                return pdx, pdy
            else:
                del self.path_memory[unit_id] # Bloqué aussi, on oublie

        # Chercher nouveau contournement (8 directions)
        all_dirs = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        # Classés par proximité avec la direction voulue (produit scalaire approx)
        all_dirs.sort(key=lambda d: -(d[0]*dx + d[1]*dy))
        
        for adx, ady in all_dirs:
            if (adx == dx and ady == dy): continue # Déjà testé
            if not self._is_blocked(unit, adx, ady, obstacles, tile):
                self.path_memory[unit_id] = (adx, ady)
                return adx, ady
                
        return 0, 0

    def _wiggle(self, unit, obstacles, tile):
        """Essaie de bouger dans une direction libre au hasard si bloqué."""
        all_dirs = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        random.shuffle(all_dirs)
        for dx, dy in all_dirs:
            if not self._is_blocked(unit, dx, dy, obstacles, tile):
                return dx, dy
        return None

    def _is_blocked(self, unit, dx, dy, obstacles, tile):
        fx = unit.rect.centerx + dx * tile * 0.9
        fy = unit.rect.centery + dy * tile * 0.9
        for o in obstacles:
            if o is unit: continue
            if math.hypot(o.rect.centerx - fx, o.rect.centery - fy) < tile * 0.8:
                return True
        return False
        
    def _is_blocked_prediction(self, unit, dx, dy, obstacles, tile, map_w, map_h):
        """Vérifie collision et limites de map."""
        fx = unit.rect.centerx + dx * tile
        fy = unit.rect.centery + dy * tile
        if not (0 <= fx < map_w * tile and 0 <= fy < map_h * tile): return True
        return self._is_blocked(unit, dx, dy, obstacles, tile)

    @staticmethod
    def _distance(a, b):
        return math.hypot(b.rect.centerx - a.rect.centerx, b.rect.centery - a.rect.centery)
