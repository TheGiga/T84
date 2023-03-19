from enum import Enum
from typing import TypeVar

from src.base_types import Unique

A = TypeVar("A", bound='Achievement')


class Achievement(Unique):
    def __init__(self, uid: int, name: str, description: str, secret: bool = False):
        self.name = name
        self.description = description
        self.secret = secret
        super().__init__(uid, self)

    def __str__(self):
        return f'🔹 {self.name}'

    def __repr__(self):
        return self.__str__()

    @property
    def fake_id(self):
        return self.uid - 2000


class Achievements(Enum):
    LVL_1 = Achievement(2001, "Це тільки початок!", "Отримайте перший рівень")

    # 2002 <...> 2006 are empty due to deletion of message count achievements.

    LVL_50 = Achievement(2007, "Богоподобний", "Отримайте 50-ий рівень.")
    SKULL_EMOJI = Achievement(2008, "💀", "Поставте реакцію-емодзі черепа.", True)
    BASE = Achievement(2009, "База", "Поставте реакцію-емодзі кавуна.", True)

    LVL_100 = Achievement(2010, "Міша, це піздець, давай по новой.", "Досягти 100-ого рівню!")

    LADNO = Achievement(2011, "Ладно.", "Подивитися інформацію про це досягнення.")
    INTERESTED = Achievement(2012, "Заінтересований в досягненнях.", "Подивитися інформацію про любе досягнення.")
    BALANCE_CHECKER = Achievement(2013, "А шо так мало?", "Подивитися свій баланс.", True)
    BOMBAS = Achievement(2014, "Хто тут бомбить Бімбас?", "Поставити емодзі бомби.", True)
