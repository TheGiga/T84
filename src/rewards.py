from typing import Union
from src.models import User


class RewardValue:
    def __init__(self, code: str, payload: Union[str, int]):
        self.code: str = code
        self.payload = payload


class Reward:
    def __init__(self, leveled: bool, value: RewardValue):
        self.leveled: bool = leveled
        self.value: RewardValue = value

    async def apply_reward(self, user: User) -> RewardValue:
        """
        :param user: src.models.User
        :return: RewardValue(code, payload): Code - string name of reward type, payload - it's actual value
        """

        match self.value.code:
            case "role":
                discord_instance = await user.get_discord_instance()

                role = discord_instance.guild.get_role(self.value.payload)

                if role is not None:
                    await discord_instance.add_roles(role, reason=f"Нагорода за рівень.")

                return self.value

            case "balance":
                await user.add_balance(amount=self.value.payload)
                return self.value

            case "achievement":
                await user.add_achievement(value=self.value, notify_user=True)
                return self.value


class Achievement:
    def __init__(self, identifier: int, text: str, long_text: str, secret: bool = False):
        self.identifier: int = identifier
        self.text: str = text
        self.long_text: str = long_text
        self.secret: bool = secret

    def __str__(self):
        return f'Досягнення: `{self.text}`'


leveled_awards = {  # Leveled
    1: [
        Reward(True, RewardValue("role", 1030995469163311186)),
        Reward(True, RewardValue("achievement", 1))
    ],
    5: [Reward(True, RewardValue("role", 1030996020747845662))],
    10: [Reward(True, RewardValue("role", 1030996194677227580))],
    15: [Reward(True, RewardValue("role", 1031205846073495552))],
    20: [Reward(True, RewardValue("role", 1031205992563757087))],
    25: [Reward(True, RewardValue("role", 1036956349080277042))],
    30: [Reward(True, RewardValue("role", 1031206572363350026))],
    35: [Reward(True, RewardValue("role", 1036956482123616276))],
    40: [Reward(True, RewardValue("role", 1031206146687639592))],
    45: [Reward(True, RewardValue("role", 1036956817516933120))]
}

achievements = {
    1: Achievement(1, "Це тільки початок!", "Отримайте перший рівень")
}


def get_formatted_reward_string(value: RewardValue) -> str:
    match value.code:
        case "role":
            return f"\🟢 <@&{value.payload}>"
        case "balance":
            return f'\🟡 {value.payload} 🪙'
        case "achievement":
            return f'\🔵 {str(achievements.get(value.payload))}'
