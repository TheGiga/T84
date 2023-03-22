PARENT_GUILD: int = 997857861705146368
PARENT_GUILD_MAIN_CHAT: int = 997857862141345804

TESTING_BOT: int = 996288139620524093
BACKEND_GUILD: int = 1043609397672288329
BACKEND_CHAT: int = 1043609400641859589

IDEAS_CHANNEL: int = 1043609400641859589  # Not used for now.

PG_INVITE: str = "https://discord.gg/8GHx6ak8cs"

ADMINS: list[int] = [352062534469156864, 690237585372610560]

cogs: list = [
    "help",
    "admin",
    "profile",
    "rewards",
    "leveling",
    "gambling",
    "moderation",
    "battlepass",
    "chat_events",
    "achievements",
    "interactive_views"
]

# Filter
BLACKLIST: list = ["🇿", "🇻", "🇷🇺"]

# Events
EVENT_CHANNEL_ID: int = PARENT_GUILD_MAIN_CHAT
FLAG_EVENT_PRIZE: int = 50

# Leveling

XP_BASE = 13
XP_MULTIPLIER = 0.25

# Self Roles

SELF_ROLES_CHANNEL_ID: int = 997882210772324433
SELF_ROLES_IDS: list[int] = [
    997873530395959398,
    997873519612403782,
    997873508354883584,
    1082031852933628045,  # івенти
    1082030848687210526  # записи чітера
]

# BP
CURRENT_BP_SEASON: int = 1

BP_XP_PER_LEVEL: int = 1000
BP_XP_PER_MESSAGE: int = 25
BP_PREMIUM_COST: int = 39 # In 💎 Premium currency