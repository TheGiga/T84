PARENT_GUILD: int = 997857861705146368  # 1043609397672288329
PARENT_GUILD_MAIN_CHAT: int = 997857862141345804

TESTING_GUILD: int = 1043609397672288329
TESTING_BOT: int = 996288139620524093

BACKEND_GUILD: int = 1043609397672288329

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
]

# Filter
BLACKLIST: list = ["🇿", "🇻", "🇷🇺"]

# Events
EVENT_CHANNEL_ID: int = PARENT_GUILD_MAIN_CHAT
EVENT_CHANNEL_ID_TESTING: int = 804835574515105834
FLAG_EVENT_PRIZE: int = 10


# Leveling

XP_MULTIPLIER = 0.25
