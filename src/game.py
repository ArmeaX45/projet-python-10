"""File: game.py"""

import pygame
import curses
import time
import threading

# Import des unités
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

class Game():
    def __init__(self, game_map, width, height):
        
        self.map = game_map
        
        # self.general_team0 = general_team0
        # self.general_team1 = general_team1
        
        self.width = width
        self.height = height
        self.grid = [['-' for _ in range(self.width)] for _ in range(self.height)]
        
        self.all_soldats = pygame.sprite.Group()
        
        self.lock = threading.Lock()
    
    
    def create_soldat(self):
        tous_mes_soldats = (
            [(Halberdier(x, y, 0)) for x in range(0, 10) for y in range(0, 10)] +
            [(Paladin(x, y, 1)) for x in range(0, 10) for y in range(10, 20)] +
            [(Arbalester(x, y, 1)) for x in range(10, 20) for y in range(0, 10)]
            )
        
        for soldat in tous_mes_soldats:
            self.add_to_soldat_group(soldat)
            self.add_on_grid(soldat)
    
    
    def check_unit(self):
        units = []
        for soldat in self.all_soldats:
            units.append(soldat)
        return units
    
    
    def add_on_grid(self, soldat):
        if soldat.is_alive:
            grid_y = soldat.rect.y // soldat.rect.height
            grid_x = soldat.rect.x // soldat.rect.width

            self.grid[grid_y][grid_x] = soldat.tag


    def show_grid(self, stdscr):
        for y, line in enumerate(self.grid):
            for x, tag in enumerate(line):
                stdscr.addstr(y+1, x * 2, tag) # y+1 because the first line is the title so we add an offset
        stdscr.refresh()


    def remove_soldat(self, soldat):
        self.all_soldats.remove(soldat)
        
        grid_y = soldat.rect.y // soldat.rect.height
        grid_x = soldat.rect.x // soldat.rect.width

        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            self.grid[grid_y][grid_x] = '-'


    def start_cmd(self, stdscr):
        curses.curs_set(0)  # Hide the cursor
        stdscr.nodelay(True)  # getch()
        
        running = True
        while running:
            stdscr.clear()      # Clear the screen

            for soldat in list(self.all_soldats):   # copy group
                if not soldat.is_alive:
                    self.remove_soldat(soldat)

            with self.lock:
                self.grid = [['-' for _ in range(self.width)] for _ in range(self.height)]
                for soldat in self.all_soldats:
                    self.add_on_grid(soldat)
    
                self.show_grid(stdscr)

            stdscr.refresh()    # Refresh the screen
            
            key = stdscr.getch()
            if key == ord('q'):  
                break
            
            time.sleep(0.2)
        
        
    def add_to_soldat_group(self, soldat):
        self.all_soldats.add(soldat)








