import discord

class DefaultEmbed(discord.Embed):
    def __init__(self):
        super().__init__()

        self.colour = discord.Colour.from_rgb(43, 45, 49)
        self.set_footer(text="by gigalegit-#0880")
        self.timestamp = discord.utils.utcnow()


from .bot import bot_instance, T84ApplicationContext
from .errors import *
from .battlepass import BattlePassEnum
from .utils import *
