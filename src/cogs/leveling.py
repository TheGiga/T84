import random

import discord
from discord.ext import tasks

from src.models import Guild, User
from src import DefaultEmbed


class Leveling(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.cache = []

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id in self.cache or message.author.bot:
            return

        await Guild.get_or_create(discord_id=message.guild.id)
        user, _ = await User.get_or_create(discord_id=message.author.id)

        xp = random.randint(4, 6)

        user.xp += xp
        await user.save()

        lvl, affected = await user.update_levels()

        if affected:
            embed = DefaultEmbed()
            embed.description = f"**Ви досягли нового рівню!**"
            embed.add_field(name='⚖ Рівень', value=f"`{lvl}`")
            embed.add_field(name='🎈 Досвід', value=f'`{user.xp}`')

            try:
                await message.reply(
                    embed=embed,
                    content=f"{message.author.mention}",
                    delete_after=10.0
                )
            except discord.Forbidden:
                pass

        self.cache.append(user.discord_id)

    @tasks.loop(minutes=2)
    async def caching_loop(self):
        self.cache.clear()


def setup(bot: discord.Bot):
    bot.add_cog(Leveling(bot=bot))
