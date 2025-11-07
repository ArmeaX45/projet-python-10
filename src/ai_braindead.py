# src/ai_braindead.py
from typing import Dict, List, Optional, TYPE_CHECKING
from .ai_base import General, Order, OrderType, dist2_tiles

if TYPE_CHECKING:
    from .soldat import Soldat

class CaptainBraindead(General):
    name = "BRAINDEAD"

    def decide(self, my_player_id: int, all_units: List["Soldat"]) -> Dict[int, Order]:
        orders: Dict[int, Order] = {}
        allies = [u for u in all_units if getattr(u, "owner", None) == my_player_id and u.is_alive]
        enemies = [u for u in all_units if getattr(u, "owner", None) != my_player_id and u.is_alive]

        for me in allies:
            # cherche un ennemi à la fois : visible ET à portée
            target = None
            for e in enemies:
                if self._in_los(me, e) and self._in_range(me, e):
                    target = e
                    break

            if target:
                orders[id(me)] = Order(type=OrderType.ATTACK, target_unit=target)
            else:
                orders[id(me)] = Order(type=OrderType.HOLD)
        return orders

    def _in_los(self, me: "Soldat", e: "Soldat") -> bool:
        return dist2_tiles(self._tile(me), self._tile(e)) <= (me.vision_range ** 2)

    def _in_range(self, me: "Soldat", e: "Soldat") -> bool:
        return dist2_tiles(self._tile(me), self._tile(e)) <= (max(0, me.attack_range) ** 2)

    def _tile(self, u: "Soldat"):
        tw, th = u.rect.width, u.rect.height
        return (u.rect.x // tw, u.rect.y // th)
