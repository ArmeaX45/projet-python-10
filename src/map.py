"""File: map.py"""

import pygame


class map():
  def __init__(self, hauteur = 120, largeur = 120):
    self.width = largeur
    self.height = hauteur
    self.matrice = [[ '-' for _ in range(0, self.widht) ]  for _ in range(0, self.height)]
  
  def add_on_grid(self, soldat):
        grid_y = soldat.rect.y // soldat.rect.height
        grid_x = soldat.rect.x // soldat.rect.width
        
        self.grid[grid_y][grid_x] = soldat.tag

  









