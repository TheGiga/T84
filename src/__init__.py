import discord

class DefaultEmbed(discord.Embed):
    def __init__(self):
        super().__init__()

        self.colour = discord.Colour.embed_background()
        self.set_footer(text="by gigalegit-#0880")
        self.timestamp = discord.utils.utcnow()


from .bot import bot_instance, T84ApplicationContext
from .errors import *
