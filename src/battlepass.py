from abc import ABC
from collections.abc import Iterable
from typing import Union, TYPE_CHECKING

from src.rewards import RoleReward, AchievementReward, BalanceReward, PremiumBalanceReward

if TYPE_CHECKING:
    from src.models import User

class BattlePassItem:
    def __init__(
            self, name: str,
            reward: Union['RoleReward', 'AchievementReward', 'BalanceReward', 'PremiumBalanceReward']
    ):
        self.name = name
        self.reward = reward

    def __repr__(self):
        return f'BattlePassItem({self.name=}, {self.reward=})'

    def __str__(self):
        return self.reward.__str__()

class BattlePassItemList(Iterable, ABC):
    def __init__(
            self,
            *items: BattlePassItem,
            paid: bool
    ):
        self._items: tuple[BattlePassItem] = items
        self.paid: bool = paid

    def __iter__(self):
        for _item in self._items:
            yield _item

    def __str__(self):
        to_return = ""

        for _item in self._items:
            to_return += f"• {_item}\n"

        return to_return.removesuffix("\n")

    async def apply_all(self, user: 'User'):
        for _item in self._items:
            await _item.reward.apply(user=user)


BPI = BattlePassItem
BPIL = BattlePassItemList

class BattlePassLevels:
    PAID_INSTANT = BPIL(
        BPI("🔻 Роль | Преміум Battle-pass #1", RoleReward(1109936141861404802)),
        paid=True
    )

    F = BPIL(
            BPI("🔸 Валюта | 500 💸", BalanceReward(500)),
            paid=False
    ) # Filler
    FP = BPIL(
            BPI("🔸 Валюта | 250 💸", BalanceReward(250)),
            paid=True
    ) # Paid Filler

    __items__ = {
        1: F, 2: FP, 3: FP, 4: F,

        5: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Гном", RoleReward(1104836790709387355)),
            paid=False
        ),

        6: FP, 7: BPIL(BPI("🔸 Преміум-валюта | 5 💎", PremiumBalanceReward(5)), paid=True), 8: F, 9: F,

        10: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Шкарпетка Залужного", RoleReward(1064265477490233554)),
            paid=True
        ),

        11: FP, 12: F, 13: F, 14: FP,

        15: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Кабанчик \"Донбасік\"", RoleReward(1109592275798990848)),
            paid=True
        ),

        16: F, 17: FP, 18: FP, 19: F,

        20: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Танк \"T-72\"", RoleReward(1076135022379143208)),
            paid=False
        ),

        21: FP, 22: FP, 23: F, 24: F,

        25: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Акція \"ROSHEN\"", RoleReward(1064265157972328623)),
            paid=True
        ),

        26: FP, 27: BPIL(BPI("🔸 Преміум-валюта | 5 💎", PremiumBalanceReward(5)), paid=False), 28: F, 29: F,

        30: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Закуска \"Пікнік (Куряча)\"", RoleReward(1109932812091543673)),
            paid=False
        ),

        31: F, 32: FP, 33: FP, 34: F,

        35: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | ФОП Дніпро", RoleReward(1109958849542246551)),
            paid=False
        ),

        36: F, 37: FP, 38: FP, 39: F,

        40: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Одесса", RoleReward(1109961143792971798)),
            paid=False
        ),

        41: FP, 42: F, 43: F, 44: FP,

        45: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Комуняка", RoleReward(1109962842075041843)),
            paid=False
        ),

        46: F, 47: BPIL(BPI("🔸 Преміум-валюта | 5 💎", PremiumBalanceReward(5)), paid=True), 48: FP,

        49: BPIL(
            BPI("🔻 Роль | Буржуй-Капиталист", RoleReward(1109963343063683180)),
            paid=False
        ),

        50: BPIL(
            BPI("🔸 Валюта | 1000 💸", BalanceReward(1000)),
            BPI("🔻 Роль | Мавпа-Анархист", RoleReward(1109963933030305852)),
            paid=True
        )
    }

    @classmethod
    def get_by_level(cls, level: int) -> Union['BattlePassItemList', None]:
        try:
            return cls.__items__[level]
        except KeyError:
            return None
