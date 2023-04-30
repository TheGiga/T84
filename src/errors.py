import discord


class GuildNotWhitelisted(discord.ApplicationCommandError):
    pass

class NotEnoughCurrency(discord.ApplicationCommandError):
    pass

class NotEnoughPremiumCurrency(discord.ApplicationCommandError):
    pass

class MaxMultiplierLimit(discord.ApplicationCommandError):
    pass

class UniqueItemNotFound(Exception):
    pass

class BattlePassSeasonNotFound(Exception):
    pass

class CouldNotSendDM(Exception):
    pass