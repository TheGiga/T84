from enum import Enum
from typing import TypeVar, Type

from src.base_types import Unique, Inventoriable
from src.models import User

T = TypeVar("T", bound="ShopItem")


class ItemValue:
    def __init__(self, code: str, payload):
        self.code = code
        self.payload = payload


class ShopItem(Unique, Inventoriable):
    def __init__(self, uid: int, label: str, cost: int, emoji: str, value: ItemValue, description: str = None):
        self.label = label
        self.cost = cost

        self.value: ItemValue = value

        self.emoji = emoji
        self.description = description

        super().__init__(uid, self)

    def __str__(self):
        return f'🔻 {self.label}'

    def __repr__(self):
        return self.__str__

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

                return self.value

        # TODO: Add other items


class ShopItems(Enum):
    ROLE_PIZZA = ShopItem(
        3001, "Pizza", 1499, "🍕", ItemValue("roles", 1041868323710840873)
    )

    ROLE_BURGER = ShopItem(
        3002, "Burger", 1999, "🍔", ItemValue("roles", 1042198043992281118)
    )

    ROLE_LEGEND_OF_BOMBASS = ShopItem(
        3003, "Пиво \"Легенда Донбасу\"", 2999, "🍺", ItemValue("roles", 1043201573762908270),
        description="Те саме, ЛЕГЕНДАРНЕ пиво - тепер може стати украсою вашого профілю!"
    )

    @classmethod
    def get_from_id(cls: Type[T], identifier: int) -> T | None:
        for name, value in cls.__dict__.items():
            try:
                if name.startswith("_"):
                    continue

                if value.value.identifier == identifier:
                    return value.value
            except AttributeError:
                continue

        return None
