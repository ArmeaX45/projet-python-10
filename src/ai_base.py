# src/ai_base.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, Dict, List, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .soldat import Soldat 

Vec2 = Tuple[int, int]  # coordonnées en tuiles (x, y)
UnitId = int

class OrderType(Enum):
    HOLD = auto()
    MOVE = auto()
    ATTACK = auto()

@dataclass
class Order:
    type: OrderType
    target_pos: Optional[Vec2] = None
    target_unit: Optional["Soldat"] = None  # forward ref pour éviter import cycle

def dist2_tiles(a: Vec2, b: Vec2) -> int:
    dx, dy = a[0] - b[0], a[1] - b[1]
    return dx*dx + dy*dy

class General:
    name = "ABSTRACT"
    def decide(self, my_player_id: int, all_units: List["Soldat"]) -> Dict[int, Order]:
        """Retourne un dictionnaire {soldat_id: Order} pour les unités alliées."""
        raise NotImplementedError
