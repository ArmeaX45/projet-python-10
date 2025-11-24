"""File: map.py"""

import pygame
import curses
import time
import threading

class Map():
    def __init__(self):
        self.width = 12
        self.height = 12
        self.grid = [['-' for _ in range(self.width)] for _ in range(self.height)]
        
        self.all_soldats = pygame.sprite.Group()
        
        self.rect = None
        self.image_lien = "./assets/mamap.png"
        
        self.lock = threading.Lock()
        
        try:
            # Charge l'image et la convertit pour un affichage rapide
            self.image = pygame.image.load(self.image_lien)
            # Récupère le rectangle (position/taille) de l'image
            self.rect = self.image.get_rect()
            self.rect.topleft = (0, 0) # Positionne l'image au coin (0,0)
    
        except pygame.error as e:
            print(f"Erreur : Impossible de charger l'image {self.image_lien}")
            print(e)
    
    
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
                self.show_grid(stdscr)

            stdscr.refresh()    # Refresh the screen
            stdscr.getch()      # Waiting for a key press
            
            key = stdscr.getch()
            if key == ord('q'):  
                break
            
            time.sleep(0.2)
        
        
    def add_to_soldat_group(self, soldat):
        self.all_soldats.add(soldat)


    def draw_map(self, image):
        if self.image:
            image.blit(self.image, self.rect)








