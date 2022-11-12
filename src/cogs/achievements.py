import discord
from discord import guild_only
from typing import Union

from src import DefaultEmbed
from src.bot import T84
from src.rewards import Achievement, Achievements as AchievementsEnum


class Achievements(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @guild_only()
    @discord.slash_command(name='achievement', description='⭐ Подивитися інформацію про досягнення.')
    async def achievement(
            self, ctx: discord.ApplicationContext, identifier: discord.Option(
                int, name='id', description="Номер досягнення. Усі досягнення пронумеровані по порядку."
            )
    ):
        achievement: Union[Achievement, None] = AchievementsEnum.get_from_id(identifier)

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


def setup(bot: T84):
    bot.add_cog(Achievements(bot=bot))
