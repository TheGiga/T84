import random
import discord
from typing import Any
from discord import guild_only
from discord.ext import tasks
from tortoise.queryset import QuerySet

from src.bot import T84
from src.models import Guild, User
from src import DefaultEmbed


class Leveling(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot
        self.cache = []
        self.caching_loop.start()

    @guild_only()
    @discord.slash_command(name='top', description='🎈 Список лідерів по рівню.')
    async def top(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        query_set: list[User, Any] = await QuerySet(User).order_by('xp')
        query_set.reverse()

        leaderboard = ""
        i = 1

        for user in query_set:
            discord_user = await user.get_discord_instance()
            leaderboard += f"{i}. `Lvl. {user.level}` " \
                           f"{discord_user.mention if discord_user is not None else user.discord_id}: `{user.xp} XP`\n"

            if i == 10:
                break

            i += 1

        embed = DefaultEmbed()
        embed.title = "🎈 Топ 10 учасників за рівнем"
        embed.description = leaderboard

        await ctx.respond(embed=embed)

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return

        if message.author.id in self.cache or message.author.bot:
            return

        await Guild.get_or_create(discord_id=message.guild.id)
        user, _ = await User.get_or_create(discord_id=message.author.id)

        xp = random.randint(9, 13)

        await user.add_xp(xp)

        lvl, affected, rewards = await user.update_levels(guild=message.guild)

        if affected:

            desc = f"**Ви досягли нового рівню!**\n\nПропишіть </profile:1031212782437290054> щоб " \
                f"подивится повну статистику свого профілю."

            if rewards is not None:
                desc += f"\n\n**Нагороди**: {rewards}"

            embed = DefaultEmbed()
            embed.description = desc

            embed.add_field(name='⚖ Рівень', value=f"`{lvl}`")
            embed.add_field(name='🎈 Досвід', value=f'`{user.xp}`')

            try:
                await message.reply(
                    embed=embed,
                    content=f"{message.author.mention}",
                    delete_after=20.0
                )
            except discord.HTTPException:
                pass

        self.cache.append(user.discord_id)

    @tasks.loop(minutes=2)
    async def caching_loop(self):
        self.cache.clear()


def setup(bot: T84):
    bot.add_cog(Leveling(bot=bot))
