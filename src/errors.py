import logging
import discord


class GuildNotWhitelisted(discord.ApplicationCommandError):
    pass

class NotEnoughPremiumCurrency(discord.ApplicationCommandError):
    pass

class MaxMultiplierLimit(discord.ApplicationCommandError):
    pass

class UniqueIdAlreadyTaken(Exception):
    def __init__(self, uid):
        logging.critical(f"Unique class with UID {uid} already registered!")


class UniqueItemNotFound(Exception):
    pass

class BattlePassSeasonNotFound(Exception):
    pass

class CouldNotSendDM(Exception):
    pass