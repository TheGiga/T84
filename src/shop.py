from enum import Enum
from typing import TypeVar, Type

from src.models import User

T = TypeVar("T", bound="ShopItem")


class ItemValue:
    def __init__(self, code: str, payload, payload_label: str):
        self.code = code
        self.payload = payload
        self.payload_label = payload_label


class ShopItem:
    def __init__(self, identifier: int, label: str, cost: int, emoji: str, value: ItemValue, description: str = None):
        self.identifier = identifier
        self.label = label
        self.cost = cost
        self.value = value
        self.emoji = emoji

        self.description = description

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
        1, "Pizza", 1499, "🍕", ItemValue(
            "roles", 1041868323710840873, "<@&1041868323710840873>"
        )
    )

    ROLE_BURGER = ShopItem(
        2, "Burger", 1999, "🍔", ItemValue(
            "roles", 1042198043992281118, "<@&1042198043992281118>"
        )
    )

    ROLE_LEGEND_OF_BOMBASS = ShopItem(
        3, "Пиво \"Легенда Донбасу\"", 2999, "🍺", ItemValue(
            "roles", 1043201573762908270, "<@&1043201573762908270>"
        ), description="Те саме, ЛЕГЕНДАРНЕ пиво - тепер може стати украсою вашого профілю!"
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
