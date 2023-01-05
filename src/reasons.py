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
    CONFLICTIVE_BEHAVIOUR = Reason(4, "Конфліктна поведінка / байтинг", 'timeout', td(hours=6))
    HUGE_INSULTS = Reason(5, 'Приниження / образи / інші фактори неадекватного спілкування між людьми', 'timeout',
                          td(hours=24))
    NSFW = Reason(6, 'NSFW (Not Safe for Work) контент', 'timeout', td(hours=24))
    IDIOTIC_BEHAVIOUR = Reason(7, '"Не будь довбойобом"', 'timeout', td(minutes=30))
