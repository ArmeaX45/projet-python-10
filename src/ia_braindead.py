# Project: MedievAIl BAIttle GenerAIl
# Added: Captain BrainDead AI class

import math
from soldat import Soldat

class GeneralBrainDead:
    def __init__(self, team_name="A"):
        self.team_name = team_name

    def update(self, game):
        actions = []

        for unit in game.all_soldats:
            if getattr(unit, 'team', None) != self.team_name:
                continue

            target = self._find_target_in_range(unit, game)

            if target:
                actions.append(("attack", unit, target))
                print(f"{unit.name} voit {target.name} et attaque !")
            else:
                print(f"{unit.name} ne voit personne et reste immobile.")
        return actions
    
    def _find_target_in_range(self, unit, game):
        for other in game.all_soldats:
            if other == unit or getattr(other, 'team', None) == unit.team:
                continue

            distance = self._distance(unit.rect.x, unit.rect.y, other.rect.x, other.rect.y)
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