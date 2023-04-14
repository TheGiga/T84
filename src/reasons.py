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
    CONFLICTIVE_BEHAVIOUR = Reason(3,"Конфлікти та провокаційні дії що ведуть до них", 'timeout', td(hours=6))
    INSULTS = Reason(4, 'Важкі образи по відношенню до учасників серверу.', 'timeout', td(hours=3))
    NSFW = Reason(5, 'Розповсюдження шокуючого контенту.', 'timeout', td(hours=12))
    SPAM_FLOOD = Reason(
        6, 'Спам/флуд та інші повідомлення що не несуть у собі смислового навантаження.', 'timeout', td(minutes=30)
    )
    ADS = Reason(7, "Реклама сторонніх сервесів/діскорд каналів/чатів, що не пов'язанні з ДТВУ.", 'timeout', td(hours=6))
    BAN_EVADING = Reason(8, "Обходження покарань за допомогою іншого аккаунта (твінка).", 'ban', td(days=365))

    @classmethod
    def get_from_id(cls, _id: int, /) -> Reason:
        reasons = list(cls)
        return reasons[_id - 1].value
