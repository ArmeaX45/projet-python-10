from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, Dict, List, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .soldat import Soldat 

Vec2 = Tuple[int, int]
UnitId = int


# ═══════════════════════════════════════════════════════════════════════════════
# TYPES D'ORDRES : Enumération des actions possibles pour une unité
# HOLD = reste sur place, MOVE = déplacement, ATTACK = attaque une cible
# ═══════════════════════════════════════════════════════════════════════════════
class OrderType(Enum):
    HOLD = auto()
    MOVE = auto()
    ATTACK = auto()

@dataclass
class Order:
    type: OrderType
    target_pos: Optional[Vec2] = None
    target_unit: Optional["Soldat"] = None

def dist2_tiles(a: Vec2, b: Vec2) -> int:
    dx, dy = a[0] - b[0], a[1] - b[1]
    return dx*dx + dy*dy


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE GENERAL : Classe abstraite de base pour toutes les IA
# Chaque IA doit implémenter la méthode decide() pour contrôler ses unités
# ═══════════════════════════════════════════════════════════════════════════════
class General:
    name = "ABSTRACT"
    def decide(self, my_player_id: int, all_units: List["Soldat"]) -> Dict[int, Order]:
        raise NotImplementedError
