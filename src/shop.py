from src import NotEnoughCurrency, NotEnoughPremiumCurrency
from src.models import User
from src.rewards import Reward, RoleReward


class ShopItem:
    def __init__(self, emoji: str, name: str, price: (int, bool), reward: Reward, category: str = "roles"):
        """

        :param name: string
        :param price: tuple(amount, premium currency?)
        :param reward: src.Reward => RoleReward | AchievementReward
        """
        self.emoji: str = emoji
        self.name: str = name
        self.price: int = price[0]
        self.premium: bool = price[1]
        self.category: str = category

        self.reward = reward

    async def apply(self, user: User):
        if self.premium:
            if user.premium_balance < self.price:
                raise NotEnoughPremiumCurrency

            await user.add_premium_balance(-self.price)
        else:
            if user.balance < self.price:
                raise NotEnoughCurrency

            await user.add_balance(-self.price)

        await self.reward.apply(user=user)

SHOP_CATEGORIES = {"roles"}
SHOP_ITEMS = [
    ShopItem(
        "🍕", "Роль Pizza", (999, False),
        RoleReward(1041868323710840873, inventoriable=True, key="shop_pizza_role_inv")
    ),

    ShopItem(
        "🍔", "Роль Burger", (999, False),
        RoleReward(1042198043992281118, inventoriable=True, key="shop_burger_role_inv")
    ),

    ShopItem(
        "🍻", 'Пиво "Легенда Донбасу"', (10, True),
        RoleReward(1043201573762908270, inventoriable=True, key="shop_beer_role_inv")
    )
]