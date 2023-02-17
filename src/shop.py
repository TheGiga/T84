from enum import Enum
from typing import TypeVar

from src.base_types import Unique, Inventoriable
from src.models import User

T = TypeVar("T", bound="ShopItem")


class ItemValue:
    def __init__(self, code: str, payload):
        self.code = code
        self.payload = payload


class ShopItem(Unique, Inventoriable):
    __slots__ = ('uid', 'label', 'cost', 'emoji', 'value', 'description')

    uid_starter = 3000

    def __init__(self, uid: int, label: str, cost: int, emoji: str, value: ItemValue, description: str = None):
        self.label = label
        self.cost = cost

        self.value: ItemValue = value

        self.emoji = emoji
        self.description = description

        Unique.__init__(self, uid, self)
        Inventoriable.__init__(self, self.__str__(), self.description)

    def __str__(self):
        return f'🔻 {self.label}'

    def __repr__(self):
        return self.__str__()

    async def give(self, user: User) -> ItemValue:
        """
        :param user: src.models.User
        :return: ItemValue(code, payload): Code - string name of ShopItem type, payload - it's actual value
        """

        match self.value.code:
            case "roles":
                discord_instance = await user.get_discord_instance()

                role = discord_instance.guild.get_role(self.value.payload)

                if role is not None:
                    await discord_instance.add_roles(role, reason=f"Нагорода за рівень.")

                await user.add_inventory_item(self)

                return self.value

        # TODO: Add other items


class ShopItems(Enum):
    ROLE_PIZZA = ShopItem(
        3001, "Pizza", 100, "🍕", ItemValue("roles", 1041868323710840873)
    )

    ROLE_BURGER = ShopItem(
        3002, "Burger", 120, "🍔", ItemValue("roles", 1042198043992281118)
    )

    ROLE_LEGEND_OF_BOMBASS = ShopItem(
        3003, "Пиво \"Легенда Донбасу\"", 700, "🍺", ItemValue("roles", 1043201573762908270),
        description="Те саме, ЛЕГЕНДАРНЕ пиво - тепер може стати украсою вашого профілю!"
    )

    BAYRAKTAR = ShopItem(
        3004, "Дрон \"Байрактар\"", 1300, "🛩", ItemValue(
            "roles", 1064264410463481906),
        description="Дрон \"Байрактар\" забезпечить вам яскраві види на східному напрямку!"
    )

    NOSOK = ShopItem(
        3005, "Шкарпетка Залужного", 2500, "🧦", ItemValue(
            "roles", 1064265477490233554),
        description="Шкарпетка Залужного, він загубив її десь під Херсоном."
    )

    ROSHEN = ShopItem(
        3006, "Акція \"РОШЕН\"", 10000, "🍫", ItemValue(
            "roles", 1064265157972328623),
        description="Шматок акції компанії ROSHEN. А може то пастка Порошенка ¯\\_(ツ)_/¯"
    )



