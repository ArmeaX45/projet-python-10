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
    
    def create_soldat(self, config):
        """
        Crée les soldats en formation RECTANGLE (blocs).
        """
        self.all_soldats.empty()
        
        class_map = {
            "Halberdier": Halberdier,
            "Paladin": Paladin,
            "Arbalester": Arbalester
        }

        # --- FONCTION INTERNE POUR PLACER UN BLOC ---
        def place_formation_block(team_id, start_x, start_y, unit_class, count, direction_x):
            """
            Place 'count' soldats en carré/rectangle à partir de (start_x, start_y).
            direction_x : 1 pour aller vers la droite (Team 0), -1 pour la gauche (Team 1).
            Retourne le Y final pour savoir où placer le groupe suivant.
            """
            if count <= 0: return start_y

            # On définit la largeur du rectangle (racine carrée pour faire un carré)
            # Ex: 10 soldats -> largeur 4 (3 rangées de 4, 4, 2)
            rect_width = math.ceil(math.sqrt(count))
            
            units_placed = 0
            current_row = 0
            
            while units_placed < count:
                for col in range(rect_width):
                    if units_placed >= count: 
                        break
                    
                    # Calcul des coordonnées
                    # Team 0 : X augmente. Team 1 : X diminue.
                    px = start_x + (col * direction_x)
                    py = start_y + current_row
                    
                    # Vérification pour rester dans la carte
                    if 0 <= px < self.width and 0 <= py < self.height:
                        soldat = unit_class(px, py, team_id)
                        self.add_to_soldat_group(soldat)
                    
                    units_placed += 1
                current_row += 1
            
            # On retourne la position Y juste après ce bloc (+1 pour espacer)
            return start_y + current_row + 1

        # --- PLACEMENT ÉQUIPE 0 (GAUCHE) ---
        current_y = 2
        base_x = 2 # On commence un peu décollé du bord gauche
        
        for unit_name, count in config[0].items():
            # Estimation simple : est-ce que ça rentre en hauteur ?
            # Si non, on décale tout le bloc vers la droite (nouvelle colonne de formations)
            estimated_height = math.ceil(count / math.ceil(math.sqrt(count))) if count > 0 else 0
            
            if current_y + estimated_height > self.height:
                current_y = 2
                base_x += 6  # On décale vers la droite pour la nouvelle colonne
            
            # On place le bloc
            current_y = place_formation_block(0, base_x, current_y, class_map[unit_name], count, 1)

        # --- PLACEMENT ÉQUIPE 1 (DROITE) ---
        current_y = 2
        base_x = self.width - 3 # On commence un peu décollé du bord droit
        
        for unit_name, count in config[1].items():
            estimated_height = math.ceil(count / math.ceil(math.sqrt(count))) if count > 0 else 0
            
            if current_y + estimated_height > self.height:
                current_y = 2
                base_x -= 6 # On décale vers la gauche pour la nouvelle colonne
            
            # On place le bloc (direction -1)
            current_y = place_formation_block(1, base_x, current_y, class_map[unit_name], count, -1)

        # Ajout final sur la grille logique pour l'IA
        for soldat in self.all_soldats:
            self.add_on_grid(soldat)
    
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