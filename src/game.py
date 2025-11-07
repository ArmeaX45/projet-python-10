# src/game.py
import pygame
import curses

from .ai_base import OrderType

class Game:
    def __init__(self):
        self.width = 12
        self.height = 12
        self.grid = [['-' for _ in range(self.width)] for _ in range(self.height)]
        self.all_soldats = pygame.sprite.Group()

        # Généraux (injectés depuis main.py)
        self.general_p0 = None
        self.general_p1 = None

    def add_on_grid(self, soldat):
        """Pose le tag de l'unité sur la grille si elle est dans les bornes."""
        grid_y = soldat.rect.y // soldat.rect.height
        grid_x = soldat.rect.x // soldat.rect.width
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.grid[grid_y][grid_x] = soldat.tag

    def show_grid(self, stdscr):
        """Affiche la grille dans le terminal en respectant la taille de la fenêtre."""
        max_y, max_x = stdscr.getmaxyx()
        for y, line in enumerate(self.grid):
            if y + 1 >= max_y:
                break
            row = " ".join(line)  # ex: "- - - P - - ..."
            stdscr.addstr(y + 1, 0, row[:max_x - 1])
        stdscr.refresh()

    def start_cmd(self, stdscr):
        """Affichage statique (si tu veux juste montrer la grille une fois)."""
        curses.curs_set(0)
        stdscr.clear()
        self.show_grid(stdscr)
        stdscr.refresh()
        stdscr.getch()

    def add_to_soldat_group(self, soldat):
        self.all_soldats.add(soldat)

    # ====== Moteur logique d’un tick ======
    def logic_tick(self):
        """Calcule les ordres des IA et applique un pas de simulation (naïf)."""
        # 1) snapshot des unités vivantes
        units = [s for s in self.all_soldats.sprites() if getattr(s, "is_alive", True)]

        # 2) décisions des deux généraux
        orders0 = self.general_p0.decide(0, units) if self.general_p0 else {}
        orders1 = self.general_p1.decide(1, units) if self.general_p1 else {}

        # 3) application
        self._apply_orders(orders0)
        self._apply_orders(orders1)

        # 4) reconstruire la grille pour l’affichage terminal
        self.grid = [['-' for _ in range(self.width)] for _ in range(self.height)]
        for u in units:
            if u.is_alive:
                self.add_on_grid(u)

    def _apply_orders(self, orders):
        """Exécute les ordres unitaires (HOLD/MOVE/ATTACK) de manière simple."""
        for uid, order in orders.items():
            # retrouver l’objet Soldat via son id() python
            me = None
            for s in self.all_soldats:
                if id(s) == uid:
                    me = s
                    break
            if me is None or not me.is_alive:
                continue

            if order.type == OrderType.HOLD:
                continue

            elif order.type == OrderType.ATTACK and order.target_unit:
                target = order.target_unit
                if me.can_attack(target):
                    me.attack(target)
                else:
                    tx, ty = target.tile_pos()
                    me.move_towards_tile(tx, ty)

            elif order.type == OrderType.MOVE and order.target_pos:
                tx, ty = order.target_pos
                me.move_towards_tile(tx, ty)
      
    
        
    
    