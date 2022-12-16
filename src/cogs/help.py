import discord
from src.bot import T84, T84ApplicationContext


class HelpCommand(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @discord.slash_command(name='help', description='❓ Допомога по боту')
    async def help(self, ctx: T84ApplicationContext):
        await ctx.respond(embeds=self.bot.help_command())


def setup(bot: T84):
    bot.add_cog(HelpCommand(bot=bot))
