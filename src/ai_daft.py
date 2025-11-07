# src/ai_daft.py
from __future__ import annotations
from typing import Dict, List, Optional, TYPE_CHECKING
from .ai_base import General, Order, OrderType, dist2_tiles
if TYPE_CHECKING:
    from .soldat import Soldat

class MajorDaft(General):
    name = "DAFT"

    def __init__(self, retarget_period: int = 5):
        self.retarget_period = retarget_period

    def decide(self, my_player_id: int, all_units: List[Soldat]) -> Dict[int, Order]:
        orders: Dict[int, Order] = {}
        allies = [u for u in all_units if getattr(u, "owner", None) == my_player_id and u.is_alive]
        enemies = [u for u in all_units if getattr(u, "owner", None) != my_player_id and u.is_alive]

        for me in allies:
            target = self._nearest_enemy(me, enemies)   # <- plus de LOS ici
            if not target:
                orders[id(me)] = Order(OrderType.HOLD)
                continue

            if self._in_range(me, target):
                orders[id(me)] = Order(OrderType.ATTACK, target_unit=target)
            else:
                tx, ty = self._tile(target)
                orders[id(me)] = Order(OrderType.MOVE, target_pos=(tx, ty))
        return orders

    # --- helpers ---
    def _nearest_enemy(self, me: Soldat, enemies: List[Soldat]) -> Optional[Soldat]:
        mx, my = self._tile(me)
        best = None
        best_d2 = 10**9
        for e in enemies:
            d2 = dist2_tiles((mx, my), self._tile(e))
            if d2 < best_d2:
                best_d2 = d2
                best = e
        return best

    def _in_range(self, me: Soldat, e: Soldat) -> bool:
        return dist2_tiles(self._tile(me), self._tile(e)) <= (max(0, me.attack_range) ** 2)

    def _tile(self, u: Soldat):
        tw, th = u.rect.width, u.rect.height
        return (u.rect.x // tw, u.rect.y // th)

