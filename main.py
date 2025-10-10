"""File: main.py"""

from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

import pygame

halberdier = Halberdier()
paladin = Paladin()
arbalester = Arbalester()

print(halberdier)
print(paladin)
print(arbalester)

print("")
halberdier.attack(paladin)
print("")

print(halberdier)
print(paladin)
print(arbalester)



