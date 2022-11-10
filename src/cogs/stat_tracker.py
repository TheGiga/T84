import discord
from discord.ext import tasks

import config
from src.models import User


class Tracker(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.message_tracker_cache: {int: int} = {}
        self.message_tracker_cache_processing.start()

    # User good-message counter (good - messages that are likely to be informative and are in main chat)
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if len(str(message.clean_content)) < 10:
            return

        if message.channel.id != config.PARENT_GUILD_MAIN_CHAT:
            return

        cached_value = self.message_tracker_cache.get(message.author.id)

        if cached_value is None:
            self.message_tracker_cache[message.author.id] = 1
            return

        self.message_tracker_cache[message.author.id] = cached_value + 1

    @tasks.loop(minutes=5)
    async def message_tracker_cache_processing(self):
        await self.bot.wait_until_ready()
        # This method should not be precise, it's pretty rough, but I don't really need precise numbers of user msg's.

        local_cache = self.message_tracker_cache.copy()

        for key in local_cache.keys():
            user, _ = await User.get_or_create(discord_id=key)

            user.message_count += local_cache[key]
            await user.save()

        self.message_tracker_cache.clear()


def setup(bot: discord.Bot):
    bot.add_cog(Tracker(bot=bot))
