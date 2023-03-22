from src.achievements import Achievement
from src.base_types import Unique
from src.models import User


class Reward(Unique):
    def __init__(self, payload: int | str, key: str = None):
        self.payload = payload
        super().__init__(cls=self, key=key)

    def __repr__(self):
        return get_formatted_reward_string(self)


class RoleReward(Reward):
    def __init__(
            self, payload: int, hierarchy_previous: int | None = None, inventoriable: bool = False, key: str = None
    ):
        super().__init__(payload, key)
        self.hierarchy_previous = hierarchy_previous
        self.inventoriable = inventoriable

    async def apply(self, user: User, remove_previous: bool = True):
        discord_instance = await user.get_discord_instance()

        role = discord_instance.guild.get_role(self.payload)

        if role is not None:
            await discord_instance.add_roles(role, reason=f"Нагорода")

        if self.inventoriable:
            await user.add_inventory_item(self)

        if remove_previous and self.hierarchy_previous is not None:
            previous_role = discord_instance.guild.get_role(self.hierarchy_previous)

            if previous_role is not None:
                await discord_instance.remove_roles(previous_role, reason="Була видана вища нагорода.")


class AchievementReward(Reward):
    def __init__(self, payload: str, key: str = None):
        super().__init__(payload, key)

    async def apply(self, user: User):
        await user.add_achievement(achievement=Achievement.get_from_key(self.payload), notify_user=True)


class BalanceReward(Reward):
    def __init__(self, payload: int, key: str = None):
        super().__init__(payload, key)

    async def apply(self, user: User):
        await user.add_balance(amount=self.payload)


def get_formatted_reward_string(value) -> str:
    if value.__class__ == RoleReward:
        return f"` Роль ` | 🔻 <@&{value.payload}>"
    elif value.__class__ == BalanceReward:
        return f'`Валюта` | 🔸 {value.payload} 💸'
    elif value.__class__ == AchievementReward:
        return f'`Ачівка` | {str(Unique.get_from_key(value.payload))}'
    else:
        return "Unknown Type"


leveled_rewards: dict = {  # Leveled
    1: [
        RoleReward(1030995469163311186, None),
        AchievementReward("ach_lvl1"),
        BalanceReward(100)
    ],  # Солдат
    5: [RoleReward(1075846937103843329, 1030995469163311186)],  # Старший Солдат
    10: [RoleReward(1030996020747845662, 1075846937103843329)],  # Сержант
    15: [RoleReward(1075846978308681798, 1030996020747845662)],  # Штаб-Сержант
    20: [RoleReward(1030996194677227580, 1075846978308681798)],  # Лейтенант
    25: [RoleReward(1075847172207169647, 1030996194677227580)],  # Старший Лейтенант
    30: [RoleReward(1031205846073495552, 1075847172207169647)],  # Капітан
    40: [RoleReward(1036956349080277042, 1031205846073495552)],  # Підполковник
    50: [
        RoleReward(1031206572363350026, 1036956349080277042),
        AchievementReward("ach_lvl50")
    ],  # Полковник
    60: [RoleReward(1031206146687639592, 1031206572363350026)],  # Генерал-Майор
    70: [RoleReward(1075847336770682900, 1031206146687639592)],  # Генерал-Лейтенант
    80: [RoleReward(1075847306156462221, 1075847336770682900)],  # Генерал-Полковник
    90: [RoleReward(1075847339325001868, 1075847306156462221)],  # Генерал Армії
    100: [
        RoleReward(1036956817516933120, 1075847339325001868),
        AchievementReward("ach_lvl100")
    ]  # Головнокомандуючий
}

for level in range(1, 201):
    money = level * 20
    try:
        leveled_rewards[level].append(BalanceReward(money))
    except KeyError:
        leveled_rewards[level] = [BalanceReward(money)]
