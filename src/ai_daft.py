# src/ai_daft.py
import math

class MajorDaftSimple:
    def __init__(self, team_name=0): # Par défaut équipe 0
        self.team_name = team_name

    def update(self, liste_soldats_brute):
        """
        Prend ta liste complexe : [{'soldat': obj}, {'soldat': obj}]
        Renvoie des actions : [("move", unit, dx, dy), ("attack", unit, target)]
        """
        actions = []

        # 1. On extrait les objets Soldat de tes dictionnaires
        # C'est ici qu'on gère ta structure spécifique
        tous_les_objets = []
        for item in liste_soldats_brute:
            if "soldat" in item:
                tous_les_objets.append(item["soldat"])

        # 2. On trie alliés / ennemis
        allies = [u for u in tous_les_objets if getattr(u, "team", None) == self.team_name and u.is_alive]
        enemies = [u for u in tous_les_objets if getattr(u, "team", None) != self.team_name and u.is_alive]

        for unit in allies:
            if not enemies:
                continue

            target = self._nearest_enemy(unit, enemies)
            if not target:
                continue

            # Positions en cases (Grille)
            ux, uy = unit.rect.x // unit.rect.width, unit.rect.y // unit.rect.height
            tx, ty = target.rect.x // target.rect.width, target.rect.y // target.rect.height
            dist = self._distance(ux, uy, tx, ty)

            # Logique simple : Attaque ou Avance
            if dist <= max(1, unit.attack_range):
                actions.append(("attack", unit, target))
            else:
                # Calcul de direction simple
                dx = 1 if tx > ux else -1 if tx < ux else 0
                dy = 1 if ty > uy else -1 if ty < uy else 0
                
                # On évite la diagonale pour simplifier le mouvement grid
                if abs(tx - ux) > abs(ty - uy):
                    dy = 0
                else:
                    dx = 0
                    
                if dx != 0 or dy != 0:
                    actions.append(("move", unit, dx, dy))

        return actions

    def _nearest_enemy(self, unit, enemies):
        ux = unit.rect.x // unit.rect.width
        uy = unit.rect.y // unit.rect.height
        best, best_d = None, 9999
        for e in enemies:
            ex = e.rect.x // e.rect.width
            ey = e.rect.y // e.rect.height
            d = self._distance(ux, uy, ex, ey)
            if d < best_d:
                best_d = d
                best = e
        return best

    def _distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)