# game.py
import pygame
from src.ai_base import Order, ORDER_MOVE, ORDER_ATTACK, ORDER_HOLD
from src.soldat import Soldat

class Game:
    """
    Game = gestion de la logique UNIQUEMENT.
    (main.py crée les unités, la map, les IA.)
    """

    def __init__(self, game_map, general_team0=None, general_team1=None):
        self.map = game_map
        self.general_team0 = general_team0
        self.general_team1 = general_team1

        # Liste déjà gérée automatiquement par Soldat
        self.units = Soldat.instances

        # On s'assure que chaque soldat a un owner
        for u in self.units:
            if not hasattr(u, "owner"):
                u.owner = 0

    def id_to_unit(self, uid):
        for u in self.units:
            if id(u) == uid:
                return u
        return None

    def apply_order(self, unit, order):
        if order.type == ORDER_HOLD:
            return

        elif order.type == ORDER_MOVE:
            if order.target_pos:
                self.move_towards(unit, order.target_pos)

        elif order.type == ORDER_ATTACK:
            target = self.id_to_unit(order.target_id)
            if target:
                self.try_attack(unit, target)

    def move_towards(self, unit, target_pos):
        ux, uy = unit.rect.x, unit.rect.y
        tx, ty = target_pos

        dx = (1 if tx > ux else -1 if tx < ux else 0)
        dy = (1 if ty > uy else -1 if ty < uy else 0)

        # On utilise TON code de mouvement (game ne le remplace pas)
        if dx != 0 or dy != 0:
            unit.move(self.map, dx=dx, dy=dy)

    def try_attack(self, unit, target):
        if not target.is_alive:
            return

        dx = target.rect.x - unit.rect.x
        dy = target.rect.y - unit.rect.y
        dist2 = dx * dx + dy * dy

        # portée en pixels
        attack_range_px = unit.attack_range * unit.rect.width

        if dist2 <= attack_range_px * attack_range_px:
            unit.attack(target)

    def cleanup_dead(self):
        for u in list(self.units):
            if not u.is_alive:
                self.map.remove_soldat(u)

    def update_grid(self):
        # Reset
        self.map.grid = [['-' for _ in range(self.map.width)]
                         for _ in range(self.map.height)]

        # Replace tous les soldats
        for u in self.units:
            if u.is_alive:
                self.map.add_on_grid(u)

    def logic_tick(self):
        """
        1. IA génère ordres
        2. ordres appliqués
        3. morts nettoyés
        4. grille mise à jour

        Aucun affichage, aucune création.
        """

        orders = {}

        if self.general_team0:
            orders.update(self.general_team0.update(self.map))

        if self.general_team1:
            orders.update(self.general_team1.update(self.map))

        for uid, order in orders.items():
            unit = self.id_to_unit(uid)
            if unit and unit.is_alive:
                self.apply_order(unit, order)

        self.cleanup_dead()
        self.update_grid()

    def print_grid(self):
        self.map.print_grid()
