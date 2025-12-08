# src/ai_daft.py
import math
from typing import List

class MajorDaftSimple:
    def __init__(self, team_name="A"):
        self.team_name = team_name  # l’équipe contrôlée

    def update(self, map_instance):
        """Renvoie des actions (attack / move) compatibles avec ton main.py."""
        actions = []

        allies = [u for u in map_instance.all_soldats if getattr(u, "team", None) == self.team_name]
        enemies = [u for u in map_instance.all_soldats if getattr(u, "team", None) != self.team_name]

        for unit in allies:
            if not enemies:
                continue

            # --- 1) trouver l’ennemi le plus proche ---
            target = self._nearest_enemy(unit, enemies)

            # convertir positions pixels → cases
            ux = unit.rect.x // unit.rect.width
            uy = unit.rect.y // unit.rect.height

            tx = target.rect.x // target.rect.width
            ty = target.rect.y // target.rect.height

            dist = self._distance(ux, uy, tx, ty)

            # --- 2) si à portée, attaquer ---
            if dist <= max(1, unit.attack_range):
                actions.append(("attack", unit, target))
                print(f"[DAFT] {unit.name} attaque {target.name}")
            
            else:
                # --- 3) sinon avancer droit vers l’ennemi ---
                dx = 1 if tx > ux else -1 if tx < ux else 0
                dy = 1 if ty > uy else -1 if ty < uy else 0

                # priorité horizontale → mouvement plus stable
                if abs(tx - ux) > abs(ty - uy):
                    actions.append(("move", unit, dx, 0))
                else:
                    actions.append(("move", unit, 0, dy))

                print(f"[DAFT] {unit.name} se déplace vers {target.name}")

        return actions

    # ======================================
    # ============== HELPERS ===============
    # ======================================

    def _nearest_enemy(self, unit, enemies):
        ux = unit.rect.x // unit.rect.width
        uy = unit.rect.y // unit.rect.height

        best = None
        best_d = 9999

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