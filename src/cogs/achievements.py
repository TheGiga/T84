import discord
from discord import guild_only
from typing import Union

from src import DefaultEmbed
from src.rewards import achievements, Achievement


class Achievements(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @guild_only()
    @discord.slash_command(name='achievement', description='⭐ Подивитися інформацію про досягнення.')
    async def achievement(
            self, ctx: discord.ApplicationContext, identifier: discord.Option(
                int, name='id', description="Номер досягнення. Усі досягнення пронумеровані по порядку."
            )
    ):
        achievement: Union[Achievement, None] = achievements.get(identifier)

        if achievement is None:
            return await ctx.respond(content="❌ Досягнення з таким номером не знайдено!", ephemeral=True)

        if achievement.secret:
            embed = DefaultEmbed()
            embed.title = "???"
            embed.description = "*Це досягнення засекречене!*"

            return await ctx.respond(embed=embed)

        embed = DefaultEmbed()
        embed.colour = discord.Colour.blurple()

        embed.title = achievement.text
        embed.description = achievement.long_text

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Achievements(bot=bot))
