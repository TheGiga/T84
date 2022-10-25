import discord
from src import help_command_embed


class HelpCommand(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name='help', description='❓ Допомога по боту')
    async def help(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=help_command_embed())


def setup(bot: discord.Bot):
    bot.add_cog(HelpCommand(bot=bot))
