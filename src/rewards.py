from typing import Union

from src.achievements import Achievement
from src.base_types import Unique
from src.models import User


class RewardValue:
    def __init__(self, code: str, payload: Union[str, int]):
        self.code: str = code
        self.payload = payload


def get_formatted_reward_string(value: RewardValue) -> str:
    match value.code:
        case "role":
            return f"`Звання` | 🔻 <@&{value.payload}>"
        case "balance":
            return f'`Валюта` | 🔸 {value.payload} 💸'
        case "achievement":
            return f'`Ачівка` | {str(Unique.get_from_id(value.payload))}'


class Reward(Unique):
    def __init__(self, uid: int, value: RewardValue):
        self.value: RewardValue = value
        super().__init__(uid, self)

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
                await user.add_achievement(achievement=Achievement.get_from_id(self.value.payload), notify_user=True)
                return self.value


leveled_rewards = {  # Leveled
    1: [
        Reward(9001, RewardValue("role", 1030995469163311186)),
        Reward(9002, RewardValue("achievement", 2001)),
        Reward(9003, RewardValue("balance", 10))
    ],
    2: [Reward(9004, RewardValue("balance", 50))],
    3: [Reward(9005, RewardValue("balance", 70))],
    5: [
        Reward(9006, RewardValue("role", 1030996020747845662)),
        Reward(9007, RewardValue("balance", 100))
    ],
    7: [Reward(9008, RewardValue("balance", 150))],
    10: [
        Reward(9009, RewardValue("role", 1030996194677227580)),
        Reward(9010, RewardValue("balance", 250))
    ],
    12: [Reward(9011, RewardValue("balance", 350))],
    15: [
        Reward(9012, RewardValue("role", 1031205846073495552)),
        Reward(9013, RewardValue("balance", 500))
    ],
    17: [Reward(9014, RewardValue("balance", 650))],
    20: [
        Reward(9015, RewardValue("role", 1031205992563757087)),
        Reward(9016, RewardValue("balance", 800))
    ],
    23: [Reward(9017, RewardValue("balance", 1000))],
    25: [
        Reward(9018, RewardValue("role", 1036956349080277042)),
        Reward(9019, RewardValue("balance", 1250))
    ],
    30: [
        Reward(9020, RewardValue("role", 1031206572363350026)),
        Reward(9021, RewardValue("balance", 1500))
    ],
    35: [
        Reward(9022, RewardValue("role", 1036956482123616276)),
        Reward(9023, RewardValue("balance", 3000))
    ],
    40: [
        Reward(9024, RewardValue("role", 1031206146687639592)),
        Reward(9025, RewardValue("balance", 5000))
    ],
    45: [
        Reward(9026, RewardValue("role", 1036956817516933120)),
        Reward(9027, RewardValue("achievement", 2007)),
        Reward(9028, RewardValue("balance", 7500))
    ],
    50: [Reward(9029, RewardValue("balance", 9000))],
    60: [Reward(9030, RewardValue("balance", 12000))],
    70: [Reward(9031, RewardValue("balance", 17000))],
    80: [Reward(9032, RewardValue("balance", 25000))],
    90: [Reward(9033, RewardValue("balance", 35000))],
    100: [
        Reward(9034, RewardValue("balance", 50000)),
        Reward(9035, RewardValue("achievement", 2010))
    ]
}