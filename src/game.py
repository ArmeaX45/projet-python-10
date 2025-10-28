"""File: game.py"""

import pygame
import curses

class Game():
    
    def __init__(self):
        
        self.width = 12
        self.height = 12
        self.grid = [['-' for _ in range(self.width)] for _ in range(self.height)]
        
        self.all_soldats = pygame.sprite.Group()
        
        
    
    def add_on_grid(self, soldat):
        grid_y = soldat.rect.y // soldat.rect.height
        grid_x = soldat.rect.x // soldat.rect.width
        
        self.grid[grid_y][grid_x] = soldat.tag
        
    
    def show_grid(self, stdscr):
        for y, line in enumerate(self.grid):
            for x, tag in enumerate(line):
                stdscr.addstr(y+1, x * 2, tag) # y+1 because the first line is the title so we add an offset
        stdscr.refresh()
    
    
    def start_cmd(self, stdscr):
        curses.curs_set(0)  # Hide the cursor
    
        stdscr.clear()      # Clear the screen
        
        self.show_grid(stdscr)
        
        stdscr.refresh()    # Refresh the screen
        stdscr.getch()      # Waiting for a key press
        
    def add_to_soldat_group(self, soldat):
        self.all_soldats.add(soldat)
        
        
    
        
    
    