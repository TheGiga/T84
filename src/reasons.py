from datetime import timedelta as td
from enum import Enum


class Reason:
    def __init__(self, _id: int, name: str, action: str, duration: td):
        self.id = _id
        self.name = name
        self.action = action
        self.duration = duration


class Reasons(Enum):
    RUSSIAN_PROPAGANDA = Reason(1, "Проросійські терміни / символіка / пропаганда.", 'ban', td(days=365))
    OPPRESSION_BY_LANGUAGE = Reason(2, "Притискання за мовною ознакою", 'timeout', td(hours=2))
    UNVERIFIED_INFORMATION_SOURCES = Reason(3, "Публікування інформації з неперевірених джерел.", 'timeout',
                                            td(hours=24))
    CONFLICTIVE_BEHAVIOUR = Reason(4, "Конфліктна поведінка", 'timeout', td(hours=6))
    HUGE_INSULTS = Reason(5, 'Приниження людей, факт неадекватного спілкування', 'timeout',
                          td(hours=6))
    NSFW = Reason(6, 'NSFW (Not Safe for Work) контент', 'timeout', td(hours=24))
    FLOOD = Reason(7, 'Флуд', 'timeout', td(minutes=30))
    ADVERTISING = Reason(8, 'Реклама', 'timeout', td(hours=6))

    @classmethod
    def get_from_id(cls, _id: int, /) -> Reason:
        reasons = list(cls)
        return reasons[_id - 1].value
