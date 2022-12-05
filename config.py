PARENT_GUILD: int = 997857861705146368
PARENT_GUILD_MAIN_CHAT: int = 997857862141345804

TESTING_BOT: int = 996288139620524093
BACKEND_GUILD: int = 1043609397672288329
BACKEND_CHAT: int = 1043609400641859589

PG_INVITE: str = "https://discord.gg/8GHx6ak8cs"

ADMINS: list[int] = [352062534469156864, 690237585372610560]

cogs: list = [
    "src.cogs.shop",
    "src.cogs.help",
    "src.cogs.admin",
    "src.cogs.filter",
    "src.cogs.profile",
    "src.cogs.rewards",
    "src.cogs.leveling",
    "src.cogs.chat_events",
    "src.cogs.stat_tracker",
    "src.cogs.achievements",
    "src.cogs.interactive_views"
]

# Filter
BLACKLIST: list = ["🇿", "🇻", "🇷🇺"]

# Events
EVENT_CHANNEL_ID: int = PARENT_GUILD_MAIN_CHAT
FLAG_EVENT_PRIZE: int = 10

# Leveling

LEVEL_MIN_MAX = 9, 13
XP_MULTIPLIER = 0.25

# Self Roles

SELF_ROLES_CHANNEL_ID: int = 997882210772324433
SELF_ROLES_IDS: list[int] = [997873530395959398, 997873519612403782, 997873508354883584]
