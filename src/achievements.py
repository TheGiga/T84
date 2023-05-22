from enum import Enum
from typing import TypeVar

from src.base_types import Unique

A = TypeVar("A", bound='Achievement')


class Achievement(Unique):
    def __init__(self, name: str, description: str, secret: bool = False, key: str = None):
        super().__init__(cls=self, key=key)
        self.name = name
        self.description = description
        self.secret = secret

    def __str__(self):
        return f'🔹 {self.name}'

    def __repr__(self):
        return self.__str__()

class Achievements(Enum):
    LVL_1 = Achievement("Це тільки початок!", "Отримайте перший рівень", key="ach_lvl1")

    # 2002 <...> 2006 are empty due to deletion of message count achievements.

    LVL_50 = Achievement("Богоподобний", "Отримайте 50-ий рівень.", key="ach_lvl50")
    SKULL_EMOJI = Achievement("💀", "Поставте реакцію-емодзі черепа.", True, key="ach_skull")
    BASE = Achievement("База", "Поставте реакцію-емодзі кавуна.", True, key="ach_watermelon")

    LVL_100 = Achievement("Міша, це піздець, давай по новой.", "Досягти 100-ого рівню!", key="ach_lvl100")

    INTERESTED = Achievement(
        "Заінтересований в досягненнях.", "Подивитися інформацію про любе досягнення.", key="ach_interested"

    )
    BALANCE_CHECKER = Achievement("А шо так мало?", "Подивитися свій баланс.", True, key="ach_balance")
    BOMBAS = Achievement("Хто тут бомбить Бімбас?", "Поставити емодзі бомби.", True, key="ach_donbass")
