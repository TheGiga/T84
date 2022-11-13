from enum import Enum


class Achievement:
    def __init__(self, identifier: int, text: str, long_text: str, secret: bool = False):
        self.identifier: int = identifier
        self.text: str = text
        self.long_text: str = long_text
        self.secret: bool = secret

    def __str__(self):
        return f'Досягнення: `{self.text}`'


class MsgCountAchievement(Achievement):
    def __init__(self, identifier: int, text: str, long_text: str, message_count: int):
        super().__init__(identifier, text, long_text)
        self.message_count = message_count


class Achievements(Enum):
    LVL_1 = Achievement(1, "Це тільки початок!", "Отримайте перший рівень")

    MSG_1 = MsgCountAchievement(2, "Спамер I", "Написати 500 повідомлень!", 500)
    MSG_2 = MsgCountAchievement(3, "Спамер II", "Написати 1000 повідомлень!", 1000)
    MSG_3 = MsgCountAchievement(4, "Спамер III", "Написати 2000 повідомлень!", 2000)
    MSG_4 = MsgCountAchievement(5, "Спамер IV", "Написати 5000 повідомлень!", 5000)
    MSG_5 = MsgCountAchievement(6, "Спамер V", "Написати 10000 повідомлень!", 10000)

    LVL_45 = Achievement(7, "Богоподобний", "Отримайте 45-ий рівень.")
    BETA_TESTER = Achievement(8, "Бета-Тестер досягнень", "Подивіться свої досягнення в період їх бета-тесту.", True)
    BASE = Achievement(9, "База", "Поставте реакцію-емодзі кавуна.", True)

    # Spizdil s drevnego koda Egor'a, sps Krashe85 <3
    @classmethod
    def get_from_id(cls, identifier: int):
        for name, value in cls.__dict__.items():
            try:
                if name.startswith("_"):
                    continue

                if value.value.identifier == identifier:
                    return value.value
            except AttributeError:
                continue
