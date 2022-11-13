from src.rewards import leveled_awards

PARENT_GUILD: int = 804835509968568351  # 997857861705146368
PARENT_GUILD_MAIN_CHAT: int = 804835574515105834  # 997857862141345804
TESTING_GUILD: int = 804835509968568351
TESTING_BOT: int = 996288139620524093
PG_INVITE: str = "https://discord.gg/8GHx6ak8cs"

cogs: list = [
    "src.cogs.filter",
    "src.cogs.profile",
    "src.cogs.leveling",
    "src.cogs.help",
    "src.cogs.chat_events",
    "src.cogs.stat_tracker",
    "src.cogs.achievements"
]

# Filter
BLACKLIST: list = ["🇿", "🇻", "🇷🇺"]

# Events
EVENT_CHANNEL_ID: int = PARENT_GUILD_MAIN_CHAT
EVENT_CHANNEL_ID_TESTING: int = 804835574515105834
FLAG_EVENT_XP_PRIZE: int = 50


# Leveling

leveled_rewards = leveled_awards

XP_MULTIPLIER = 0.25
