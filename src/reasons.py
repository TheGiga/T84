from enum import Enum


class Reason:
    def __init__(self, _id: int, name: str):
        self.id = _id
        self.name = name


class Reasons(Enum):
    RUSSIAN_PROPAGANDA = Reason(1, "Проросійські терміни / символіка / пропаганда.")
    OPPRESSION_BY_LANGUAGE = Reason(2, "Притискання за мовною ознакою")
    CONFLICTIVE_BEHAVIOUR = Reason(3,"Конфлікти та провокаційні дії що ведуть до них")
    INSULTS = Reason(4, 'Важкі образи по відношенню до учасників серверу.')
    NSFW = Reason(5, 'Розповсюдження шокуючого контенту.')
    SPAM_FLOOD = Reason(6, 'Спам/флуд та інші повідомлення що не несуть у собі смислового навантаження.')
    ADS = Reason(7, "Реклама сторонніх сервесів/діскорд каналів/чатів, що не пов'язанні з ДТВУ.")
    BAN_EVADING = Reason(8, "Обходження покарань за допомогою іншого аккаунта (твінка).")
    NON_SERIOUS = Reason(9, "Несерйозна поведінка.")

    @classmethod
    def get_from_id(cls, _id: int, /) -> Reason:
        reasons = list(cls)
        return reasons[_id - 1].value
