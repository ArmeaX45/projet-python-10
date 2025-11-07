"""File: map.py"""

import pygame
import curses

class map():
    def __init__(self, image_lien):
        self.image = None
        self.rect = None
        
        try:
            # Charge l'image et la convertit pour un affichage rapide
            self.image = pygame.image.load(image_lien)
            # Récupère le rectangle (position/taille) de l'image
            self.rect = self.image.get_rect()
            self.rect.topleft = (0, 0) # Positionne l'image au coin (0,0)
            
        except pygame.error as e:
            print(f"Erreur : Impossible de charger l'image {image_lien}")
            print(e)
        
        
    def add_on_grid(self, soldat):
        grid_y = soldat.rect.y // soldat.rect.height
        grid_x = soldat.rect.x // soldat.rect.width
        
        self.grid[grid_y][grid_x] = soldat.tag
        
    """
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
        """
    def add_to_soldat_group(self, soldat):
        self.all_soldats.add(soldat)

    def draw_map(self, image):
        if self.image:
            image.blit(self.image, self.rect)



    








