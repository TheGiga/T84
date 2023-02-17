import logging
import discord


class GuildNotWhitelisted(discord.ApplicationCommandError):
    pass


class UniqueIdAlreadyTaken(Exception):
    def __int__(self, uid):
        logging.critical(f"Unique class with UID {uid} already registered!")


class UniqueItemNotFound(Exception):
    pass


class NotEnoughMoneyInBank(Exception):
    pass
