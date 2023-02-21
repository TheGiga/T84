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
                    await discord_instance.add_roles(role, reason=f"Покупка ролі")

                await user.add_inventory_item(self)

                return self.value

            case "multipliers":
                x = round(user.xp_multiplier + self.value.payload, 10)
                user.xp_multiplier = x

                await user.save()

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

    T72 = ShopItem(
        3007, "Танк \"Т-72\"", 7200, "💥", ItemValue(
            "roles", 1076135022379143208),
        description="Танк Т-72 стандартної модифікації, ще не літав."
    )

    BRADLEY = ShopItem(
        3008, "БМП \"Bradley\"", 3000, "🔫", ItemValue(
            "roles", 1076135025575211039),
        description='БМП Bradley - я її знайшов десь в Іраку.'
    )

    J2M5 = ShopItem(
        3009, "Винищувач \"J2M5 Raiden\"", 6500, "✈", ItemValue(
            "roles", 1076135008613433374),
        description='Винищувач "J2M5 Raiden" імператорського флоту Японії, '
                    'я його вкрав у Акамацу Садаакі поки він бухав.'
    )

    MULTIPLIER_0_1 = ShopItem(
        3101, "Множник досвіду +0.1x", 1000, "⚗", ItemValue(
            "multipliers", 0.1),
        description="Додає +0.1x до вашого загального множника досвіду. "
                    "- Перевірити можна в /profile"
    )

    MULTIPLIER_1_0 = ShopItem(
        3102, "Множник досвіду +1.0x", 9000, "⚗", ItemValue(
            "multipliers", 1.0),
        description="Додає +1.0x до вашого загального множника досвіду. "
                    "- Перевірити можна в /profile"
    )



