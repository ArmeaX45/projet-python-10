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

            # --- 1) trouver l’ennemi le plus proche (en pixels) ---
            target = self._nearest_enemy_px(unit, enemies)
            if target is None:
                continue

            # --- 2) test "à portée" en PIXELS ---
            dist_px = self._distance_px_centers(unit, target)

            # taille d'une tuile (chez toi: rect.width/height = taille sprite = taille case)
            tile = unit.rect.width

            # conversion de portée :
            # - ranged (attack_range > 0): attack_range est en "cases" dans tes unités => * tile
            # - melee (attack_range == 0): on veut du "contact", donc seuil en pixels
            if getattr(unit, "attack_range", 0) > 0:
                range_px = unit.attack_range * tile
            else:
                # contact approx: un peu plus que la moitié d'une case (ajuste 0.55-0.75 si tu veux)
                range_px = tile * 0.65

            if dist_px <= range_px:
                actions.append(("attack", unit, target))
                print(f"[DAFT] {unit.name} attaque {target.name}")
                continue

            # --- 3) sinon avancer vers l’ennemi (dx/dy comme avant, basé sur des cases) ---
            ux = unit.rect.centerx / tile
            uy = unit.rect.centery / tile
            tx = target.rect.centerx / tile
            ty = target.rect.centery / tile

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

    def _nearest_enemy_px(self, unit, enemies):
        """Choisit la cible la plus proche en PIXELS (centre à centre)."""
        best = None
        best_d2 = float("inf")

        ux, uy = unit.rect.center

        for e in enemies:
            ex, ey = e.rect.center
            dx = ex - ux
            dy = ey - uy
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best = e

        return best

    @staticmethod
    def _distance_px_centers(a, b):
        """Distance en pixels entre centres des rects."""
        ax, ay = a.rect.center
        bx, by = b.rect.center
        return math.hypot(bx - ax, by - ay)