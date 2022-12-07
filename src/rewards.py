from src.achievements import Achievement
from src.base_types import Unique
from src.models import User


def get_formatted_reward_string(value: 'Reward') -> str:
    match value.code:
        case "role":
            return f"`Звання` | 🔻 <@&{value.payload}>"
        case "balance":
            return f'`Валюта` | 🔸 {value.payload} 💸'
        case "achievement":
            return f'`Ачівка` | {str(Unique.get_from_id(value.payload))}'


class Reward(Unique):
    def __init__(self, uid: int, code: str, payload: int | str):
        self.code: str = code
        self.payload = payload
        super().__init__(uid, self)

    def __repr__(self):
        return get_formatted_reward_string(self)

    async def apply(self, user: User):
        """
        :param user: src.models.User
        """

        match self.code:
            case "role":
                discord_instance = await user.get_discord_instance()

                role = discord_instance.guild.get_role(self.payload)

                if role is not None:
                    await discord_instance.add_roles(role, reason=f"Нагорода за рівень.")

            case "balance":
                await user.add_balance(amount=self.payload)

            case "achievement":
                await user.add_achievement(achievement=Achievement.get_from_id(self.payload), notify_user=True)


leveled_rewards = {  # Leveled
    1: [
        Reward(9001, "role", 1030995469163311186),
        Reward(9002, "achievement", 2001),
        Reward(9003, "balance", 10)
    ],
    2: [Reward(9004, "balance", 50)],
    3: [Reward(9005, "balance", 70)],
    5: [
        Reward(9006, "role", 1030996020747845662),
        Reward(9007, "balance", 100)
    ],
    7: [Reward(9008, "balance", 150)],
    10: [
        Reward(9009, "role", 1030996194677227580),
        Reward(9010, "balance", 250)
    ],
    12: [Reward(9011, "balance", 350)],
    15: [
        Reward(9012, "role", 1031205846073495552),
        Reward(9013, "balance", 500)
    ],
    17: [Reward(9014, "balance", 650)],
    20: [
        Reward(9015, "role", 1031205992563757087),
        Reward(9016, "balance", 800)
    ],
    23: [Reward(9017, "balance", 1000)],
    25: [
        Reward(9018, "role", 1036956349080277042),
        Reward(9019, "balance", 1250)
    ],
    30: [
        Reward(9020, "role", 1031206572363350026),
        Reward(9021, "balance", 1500)
    ],
    35: [
        Reward(9022, "role", 1036956482123616276),
        Reward(9023, "balance", 3000)
    ],
    40: [
        Reward(9024, "role", 1031206146687639592),
        Reward(9025, "balance", 5000)
    ],
    45: [
        Reward(9026, "role", 1036956817516933120),
        Reward(9027, "achievement", 2007),
        Reward(9028, "balance", 7500)
    ],
    50: [Reward(9029, "balance", 9000)],
    60: [Reward(9030, "balance", 12000)],
    70: [Reward(9031, "balance", 17000)],
    80: [Reward(9032, "balance", 25000)],
    90: [Reward(9033, "balance", 35000)],
    100: [
        Reward(9034, "balance", 50000),
        Reward(9035, "achievement", 2010)
    ]
}