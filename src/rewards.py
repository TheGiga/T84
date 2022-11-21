from typing import Union

from src.achievements import Achievements
from src.models import User


class RewardValue:
    def __init__(self, code: str, payload: Union[str, int]):
        self.code: str = code
        self.payload = payload


class Reward:
    def __init__(self, value: RewardValue):
        self.value: RewardValue = value

    def __repr__(self):
        return get_formatted_reward_string(self.value)

    async def apply(self, user: User) -> RewardValue:
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
                await user.add_achievement(achievement=Achievements.get_from_id(self.value.payload), notify_user=True)
                return self.value


leveled_rewards = {  # Leveled
    1: [
        Reward(RewardValue("role", 1030995469163311186)),
        Reward(RewardValue("achievement", 1)),
        Reward(RewardValue("balance", 10))
    ],
    2: [Reward(RewardValue("balance", 50))],
    3: [Reward(RewardValue("balance", 70))],
    5: [
        Reward(RewardValue("role", 1030996020747845662)),
        Reward(RewardValue("balance", 100))
    ],
    7: [Reward(RewardValue("balance", 150))],
    10: [
        Reward(RewardValue("role", 1030996194677227580)),
        Reward(RewardValue("balance", 250))
    ],
    12: [Reward(RewardValue("balance", 350))],
    15: [
        Reward(RewardValue("role", 1031205846073495552)),
        Reward(RewardValue("balance", 500))
    ],
    17: [Reward(RewardValue("balance", 650))],
    20: [
        Reward(RewardValue("role", 1031205992563757087)),
        Reward(RewardValue("balance", 800))
    ],
    23: [Reward(RewardValue("balance", 1000))],
    25: [
        Reward(RewardValue("role", 1036956349080277042)),
        Reward(RewardValue("balance", 1250))
    ],
    30: [
        Reward(RewardValue("role", 1031206572363350026)),
        Reward(RewardValue("balance", 1500))
    ],
    35: [
        Reward(RewardValue("role", 1036956482123616276)),
        Reward(RewardValue("balance", 3000))
    ],
    40: [
        Reward(RewardValue("role", 1031206146687639592)),
        Reward(RewardValue("balance", 5000))
    ],
    45: [
        Reward(RewardValue("role", 1036956817516933120)),
        Reward(RewardValue("achievement", 7)),
        Reward(RewardValue("balance", 7500))
    ],
    50: [Reward(RewardValue("balance", 9000))],
    60: [Reward(RewardValue("balance", 12000))],
    70: [Reward(RewardValue("balance", 17000))],
    80: [Reward(RewardValue("balance", 25000))],
    90: [Reward(RewardValue("balance", 35000))],
    100: [Reward(RewardValue("balance", 50000))]
}


def get_formatted_reward_string(value: RewardValue) -> str:
    match value.code:
        case "role":
            return f"🟡 <@&{value.payload}>"
        case "balance":
            return f'🟢 {value.payload} 💸'
        case "achievement":
            return f'🔵 {str(Achievements.get_from_id(value.payload))}'
