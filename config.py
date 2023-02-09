PARENT_GUILD: int = 997857861705146368
PARENT_GUILD_MAIN_CHAT: int = 997857862141345804

TESTING_BOT: int = 996288139620524093
BACKEND_GUILD: int = 1043609397672288329
BACKEND_CHAT: int = 1043609400641859589

IDEAS_CHANNEL: int = 1043609400641859589  # Not used for now.

PG_INVITE: str = "https://discord.gg/8GHx6ak8cs"

ADMINS: list[int] = [352062534469156864, 690237585372610560]

cogs: list = [
    "shop",
    "help",
    "admin",
    "filter",
    "profile",
    "rewards",
    "leveling",
    "moderation",
    "chat_events",
    "stat_tracker",
    "achievements",
    "interactive_views"
]

# Filter
BLACKLIST: list = ["🇿", "🇻", "🇷🇺"]

# Events
EVENT_CHANNEL_ID: int = PARENT_GUILD_MAIN_CHAT
FLAG_EVENT_PRIZE: int = 10

# Leveling

XP_BASE = 13
XP_MULTIPLIER = 0.25

# Self Roles

SELF_ROLES_CHANNEL_ID: int = 997882210772324433
SELF_ROLES_IDS: list[int] = [997873530395959398, 997873519612403782, 997873508354883584]
