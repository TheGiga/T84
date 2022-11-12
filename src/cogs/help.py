import discord
from src.bot import T84


class HelpCommand(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @discord.slash_command(name='help', description='❓ Допомога по боту')
    async def help(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=self.bot.help_command_embed())


def setup(bot: T84):
    bot.add_cog(HelpCommand(bot=bot))
