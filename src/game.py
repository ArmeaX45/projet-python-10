"""File: game.py"""

import pygame
import curses
import time
import threading
import math  

# Import des unités
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

class Game():
    def __init__(self, game_map, width, height):
        self.map = game_map
        self.width = width
        self.height = height
        self.grid = [['-' for _ in range(self.width)] for _ in range(self.height)]
        
        self.all_soldats = pygame.sprite.Group()
        self.lock = threading.Lock()
    
    def create_soldat(self, config, ai_team0=None, ai_team1=None):
        """
        Crée les soldats avec formations définis par les IA.
        Si une IA a une méthode get_formation(), elle est utilisée.
        """
        self.all_soldats.empty()
        
        class_map = {
            "Halberdier": Halberdier,
            "Paladin": Paladin,
            "Arbalester": Arbalester
        }

        # === ÉQUIPE 0 ===
        if ai_team0 and hasattr(ai_team0, 'get_formation'):
            positions = ai_team0.get_formation(0, self.width, self.height, config[0])
            for unit_type, px, py in positions:
                if 0 <= px < self.width and 0 <= py < self.height:
                    soldat = class_map[unit_type](px, py, 0)
                    self.add_to_soldat_group(soldat)
        else:
            # Formation par défaut
            self._default_formation(0, config[0], class_map)

        # === ÉQUIPE 1 ===
        if ai_team1 and hasattr(ai_team1, 'get_formation'):
            positions = ai_team1.get_formation(1, self.width, self.height, config[1])
            for unit_type, px, py in positions:
                if 0 <= px < self.width and 0 <= py < self.height:
                    soldat = class_map[unit_type](px, py, 1)
                    self.add_to_soldat_group(soldat)
        else:
            # Formation par défaut
            self._default_formation(1, config[1], class_map)

        # Ajout final sur la grille logique pour l'IA
        for soldat in self.all_soldats:
            self.add_on_grid(soldat)

    def _default_formation(self, team_id, config, class_map):
        """Formation par défaut en bloc (colonnes successives)."""
        if team_id == 0:
            start_x = 2
            x_dir = 1
        else:
            start_x = self.width - 1 # Tout au fond à droite
            x_dir = -1
        
        current_y = 2
        col_offset = 0
        
        # ORDRE STRICT : Arbalester (Fond), Paladin (Milieu), Halberdier (Front)
        # Car plus on spawn tôt, plus on est "en arrière" (x + col_offset)
        # Wait... X augmente pour Team 0. Donc col_offset 0 = Gauche (Arrière pour Team 0).
        # Pour Team 1, X diminue. start_x = Right. col_offset * -1 => Vers gauche (Avant).
        # Ah ! Team 1 avance vers la gauche.
        # Start X = Width. Col 0 = Width. Col 1 = Width - 1.
        # Donc Col 0 est L'ARRIERE pour Team 1 aussi ?
        # Non, Team 1 est à Droite, regarde à Gauche. L'arrière est à Droite (X grand).
        # Donc Col 0 (X grand) est l'arrière.
        # Donc PREMIER spawn = ARRIERE pour les deux équipes !
        
        ordered_keys = ["Arbalester", "Paladin", "Halberdier"]
        
        for unit_name in ordered_keys:
            count = config.get(unit_name, 0)
            if count == 0: continue
            
            for _ in range(count):
                # Calcul de position
                px = start_x + (col_offset * x_dir)
                py = current_y
                
                # Placement sécurisé
                if 0 <= px < self.width and 0 <= py < self.height:
                    soldat = class_map[unit_name](px, py, team_id)
                    self.add_to_soldat_group(soldat)
                
                # Avancer curseur
                current_y += 1
                if current_y > self.height - 2:
                    current_y = 2
                    col_offset += 1
    
    def add_on_grid(self, soldat):
        if soldat.is_alive:
            grid_y = int(soldat.rect.y // soldat.rect.height)
            grid_x = int(soldat.rect.x // soldat.rect.width)
            
            if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
                self.grid[grid_y][grid_x] = soldat.tag

    def remove_soldat(self, soldat):
        self.all_soldats.remove(soldat)
        grid_y = int(soldat.rect.y // soldat.rect.height)
        grid_x = int(soldat.rect.x // soldat.rect.width)
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            self.grid[grid_y][grid_x] = '-'

    def start_cmd(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        running = True
        while running:
            stdscr.clear()
            for soldat in list(self.all_soldats):
                if not soldat.is_alive:
                    self.remove_soldat(soldat)
            
            with self.lock:
                self.grid = [['-' for _ in range(self.width)] for _ in range(self.height)]
                for soldat in self.all_soldats:
                    self.add_on_grid(soldat)
                self.show_grid(stdscr)
            
            stdscr.refresh()
            if stdscr.getch() == ord('q'): break
            time.sleep(0.2)

    def show_grid(self, stdscr):
        for y, line in enumerate(self.grid):
            line_str = "".join(line)
            try: stdscr.addstr(y, 0, line_str)
            except: pass
        
    def add_to_soldat_group(self, soldat):
        self.all_soldats.add(soldat)