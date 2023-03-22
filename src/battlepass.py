from abc import ABC
from enum import Enum
from collections.abc import Iterable
from typing import Union, TYPE_CHECKING

from src.rewards import RoleReward, AchievementReward, BalanceReward

if TYPE_CHECKING:
    from src.models import User

class BattlePassItem:
    def __init__(
            self, name: str, description: str | None, reward: Union['RoleReward', 'AchievementReward', 'BalanceReward']
    ):
        self.name = name
        self.description = description
        self.reward = reward

    def __repr__(self):
        return f'BattlePassItem({self.name=}, {self.reward=})'

    def __str__(self):
        return self.reward.__str__()

class BattlePassItemList(Iterable, ABC):
    def __init__(
            self, *items: BattlePassItem,
            paid: bool, level: int
    ):
        self._items: tuple[BattlePassItem] = items
        self.paid: bool = paid
        self.level = level

    def __iter__(self):
        for _item in self._items:
            yield _item

    def __str__(self):
        to_return = ""

        for _item in self._items:
            to_return += f"• {_item}\n".removesuffix("\n")

        return to_return

    async def apply_all(self, user: 'User'):
        for _item in self._items:
            await _item.reward.apply(user=user)


BPI = BattlePassItem
BPIL = BattlePassItemList

class BattlePassEnum(Enum):
    PAID_INSTANT = BPIL(
        BPI("🔻 Роль | Преміум Battle-pass #1", None, RoleReward(1049431166442279074)),
        paid=True, level=0
    )

    LVL_1 = BPIL(
        BPI("🔸 Валюта | 1000 💸", None, BalanceReward(1000)),
        paid=False, level=1
    )

    LVL_2 = BPIL(
        BPI("🔸 Валюта | 1000 💸", None, BalanceReward(1000)),
        paid=True, level=2
    )

    LVL_3 = BPIL(
        BPI("🔸 Валюта | 1000 💸", None, BalanceReward(1000)),
        paid=True, level=3
    )

    LVL_4 = BPIL(
        BPI("🔸 Валюта | 1000 💸", None, BalanceReward(1000)),
        paid=True, level=4
    )

    LVL_5 = BPIL(
        BPI("🔸 Валюта | 1000 💸", None, BalanceReward(1000)),
        paid=False, level=5
    )

    @classmethod
    def get_by_level(cls, level: int) -> Union['BattlePassItemList', None]:
        for item in cls:
            if item.value.level == level:
                return item.value
            continue

        return None
