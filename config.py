PARENT_GUILD: int = 997857861705146368
TESTING_GUILD: int = 804835509968568351
TESTING_BOT: int = 996288139620524093
PG_INVITE: str = "https://discord.gg/8GHx6ak8cs"

cogs: list = [
    "src.cogs.filter",
    "src.cogs.profile",
    "src.cogs.leveling",
    "src.cogs.help",
    "src.cogs.events"
]

# Filter
BLACKLIST: list = ["🇿", "🇻", "🇷🇺"]

# Events
EVENT_CHANNEL_ID: int = 997857862141345804
EVENT_CHANNEL_ID_TESTING: int = 804835574515105834
FLAG_EVENT_XP_PRIZE: int = 250


# Leveling

class Reward:
    def __init__(self, reward_type: str, value: int):
        self.reward_type = reward_type
        self.value = value


awards = {  # Roles
    1: Reward("role", 1030995469163311186),
    5: Reward("role", 1030996020747845662),
    10: Reward("role", 1030996194677227580),
    15: Reward("role", 1031205846073495552),
    20: Reward("role", 1031205992563757087),
    25: Reward("role", 1036956349080277042),
    30: Reward("role", 1031206572363350026),
    35: Reward("role", 1036956482123616276),
    40: Reward("role", 1031206146687639592),
    45: Reward("role", 1036956817516933120)
}

XP_MULTIPLIER = 0.25
