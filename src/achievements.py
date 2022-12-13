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


class MsgCountAchievement(Achievement):
    def __init__(self, uid: int, name: str, description: str, message_count: int, secret: bool = False):
        self.message_count = message_count
        super().__init__(uid, name, description, secret)


class Achievements(Enum):
    LVL_1 = Achievement(2001, "Це тільки початок!", "Отримайте перший рівень")

    MSG_1 = MsgCountAchievement(2002, "Спамер I", "Написати 500 повідомлень!", 500)
    MSG_2 = MsgCountAchievement(2003, "Спамер II", "Написати 1000 повідомлень!", 1000)
    MSG_3 = MsgCountAchievement(2004, "Спамер III", "Написати 2000 повідомлень!", 2000)
    MSG_4 = MsgCountAchievement(2005, "Спамер IV", "Написати 5000 повідомлень!", 5000)
    MSG_5 = MsgCountAchievement(2006, "Спамер V", "Написати 10000 повідомлень!", 10000)

    LVL_45 = Achievement(2007, "Богоподобний", "Отримайте 45-ий рівень.")
    SKULL_EMOJI = Achievement(2008, "💀", "Поставте реакцію-емодзі черепа.", True)
    BASE = Achievement(2009, "База", "Поставте реакцію-емодзі кавуна.", True)

    LVL_100 = Achievement(2010, "Міша, це піздець, давай по новой.", "Досягти 100-ого рівню!")

    LADNO = Achievement(2011, "Ладно.", "Подивитися інформацію про це досягнення.")
    INTERESTED = Achievement(2012, "Заінтересований в досягненнях.", "Подивитися інформацію про любе досягнення.")
    BALANCE_CHECKER = Achievement(2013, "А шо так мало?", "Подивитися свій баланс.", True)
    BOMBAS = Achievement(2014, "Хто тут бомбить Бімбас?", "Поставити емодзі бомби.", True)
