# Project: MedievAIl BAIttle GenerAIl
# Added: Captain BrainDead AI class

import math

class GeneralBrainDead:
    def __init__(self, team_name="A"):
        self.team_name = team_name # L'équipe que cette IA contrôle

    def update(self, map_instance):
        """Analyse la map et renvoie une liste d'actions pour chaque unité de l'équipe."""
        actions = []

        # On parcourt toutes les unités présentes sur la map
        for unit in map_instance.all_soldats:
            # Ignore les ennemis ou unités sans équipe
            if getattr(unit, 'team', None) != self.team_name or not unit.is_alive:
                continue
            
            # Recherche d'une cible dans le champ de vision
            target = self._find_target_in_range(unit, map_instance)

            if not target:
                print(f"{unit.name} ne voit personne et reste immobile.")
                continue
            
            ux, uy = unit.rect.x // unit.rect.width, unit.rect.y // unit.rect.height
            tx, ty = target.rect.x // target.rect.width, target.rect.y // target.rect.height
            distance = max(abs(tx - ux), abs(ty - uy))
            
            if distance <= unit.attack_range:
                actions.append(("attack", unit, target))
                print(f"{unit.name} voit {target.name} et attaque !")
            elif distance <= unit.vision_range:
                dx = 1 if tx > ux else -1 if tx < ux else 0
                dy = 1 if ty > uy else -1 if ty < uy else 0
                actions.append(("move", unit, dx, dy))
                print(f"{unit.name} avance vers {target.name} (dx={dx}, dy={dy})")
            else: 
                print(f"{unit.name} ne voit personne et reste immobile.")
        return actions
    
    def _find_target_in_range(self, unit, map_instance):
        """Trouve une unité ennemie à portée de vision."""
        for other in map_instance.all_soldats:
            if other == unit or getattr(other, 'team', None) == unit.team:
                continue

            # Calcul de distance en cases (pas en pixels)
            distance = self._distance(
                          unit.rect.x // unit.rect.width,
                          unit.rect.y // unit.rect.height,
                          other.rect.x // other.rect.width,
                          other.rect.y // other.rect.height)

            if distance <= unit.vision_range:
                return other
        return None
    
    @staticmethod
    def _distance(x1, y1, x2, y2):
        return math.sqrt((x2-x1) ** 2 + (y2-y1)**2)



""" Exemple de test minimal dans le terminal (à garder pour toi)
if __name__ == "__main__":
from src.game import Game
from src.halberdier import Halberdier
from src.paladin import Paladin


game = Game()


# Attribuer des équipes aux unités (important pour l'IA)
h = Halberdier(0, 0)
h.team = "A"
p = Paladin(5, 0)
p.team = "B"


game.add_to_soldat_group(h)
game.add_to_soldat_group(p)


ia = GeneralBrainDead(team_name="A")
ia.update(game)
"""