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
        
        # Calculer les dimensions réelles de la grille basées sur l'image de la map
        # Taille d'une case = 32 pixels (taille des sprites)
        TILE_SIZE = 32
        self.width = game_map.original_image.get_width() // TILE_SIZE
        self.height = game_map.original_image.get_height() // TILE_SIZE
        
        print(f"[GAME] Map réelle: {game_map.original_image.get_width()}x{game_map.original_image.get_height()} pixels")
        print(f"[GAME] Grille de jeu: {self.width}x{self.height} cases (tile_size={TILE_SIZE})")
        
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
        """Formation par défaut optimisée : placement tactique aux extrémités."""
        
        # Calculer le nombre total d'unités
        total_units = sum(config.values())
        if total_units == 0:
            return
        
        # ORDRE TACTIQUE : Arbalester (arrière), Paladin (milieu), Halberdier (front)
        ordered_keys = ["Arbalester", "Paladin", "Halberdier"]
        
        # Déterminer les positions de base selon l'équipe
        # self.width et self.height sont maintenant basés sur l'image réelle de la map
        if team_id == 0:
            # Équipe 0 : GAUCHE de la map (x = 0, 1, 2)
            column_positions = [0, 1, 2]
        else:
            # Équipe 1 : DROITE de la map
            column_positions = [self.width - 1, self.width - 2, self.width - 3]
        
        # Centre vertical de la map
        center_y = self.height // 2
        
        # Placer chaque type d'unité dans sa colonne dédiée
        for col_index, unit_name in enumerate(ordered_keys):
            count = config.get(unit_name, 0)
            if count == 0:
                continue
            
            # Position X de cette colonne
            px = column_positions[col_index]
            
            # Calculer les positions Y pour centrer les unités de ce type
            # Si count est pair : -count/2+0.5, -count/2+1.5, ..., +count/2-1.5, +count/2-0.5
            # Si count est impair : -count/2, ..., 0, ..., +count/2
            start_offset = -(count // 2)
            
            for i in range(count):
                # Position Y : centrer autour de center_y
                py = center_y + start_offset + i
                
                # Vérifier les limites de la map
                if 0 <= px < self.width and 0 <= py < self.height:
                    soldat = class_map[unit_name](px, py, team_id)
                    self.add_to_soldat_group(soldat)
                else:
                    # Si on dépasse les limites, essayer de placer ailleurs
                    # Chercher une position valide proche
                    for offset_y in range(-2, 3):
                        alt_py = py + offset_y
                        if 0 <= alt_py < self.height:
                            soldat = class_map[unit_name](px, alt_py, team_id)
                            self.add_to_soldat_group(soldat)
                            break
    
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