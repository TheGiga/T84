import discord
from discord.ext import tasks

from src.bot import T84
from src.models import User
from src.achievements import Achievements, MsgCountAchievement


class Tracker(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot
        self.message_tracker_cache: {int: int} = {}
        self.message_tracker_cache_processing.start()

    # User good-message counter (good - messages that are likely to be informative and are in main chat)
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if len(str(message.clean_content)) < 10:
            return

        if message.channel.id != self.bot.config.PARENT_GUILD_MAIN_CHAT:
            return

        cached_value = self.message_tracker_cache.get(message.author.id)

        if cached_value is None:
            self.message_tracker_cache[message.author.id] = 1
            return

        self.message_tracker_cache[message.author.id] = cached_value + 1

    @tasks.loop(minutes=5)
    async def message_tracker_cache_processing(self):
        if not self.bot.is_ready():
            return

        # This method should not be precise, it's pretty rough, but I don't really need precise numbers of user msg's.

        local_cache = self.message_tracker_cache.copy()

        message_count_achievements = tuple(
            ach.value for ach in Achievements if type(ach.value) is MsgCountAchievement
        )

        for key in local_cache.keys():
            user, _ = await User.get_or_create(discord_id=key)

            user.message_count += local_cache[key]
            await user.save()

            for ach in message_count_achievements:
                if user.message_count > ach.message_count:
                    await user.add_achievement(ach, notify_user=True)

        self.message_tracker_cache.clear()


def setup(bot: T84):
    bot.add_cog(Tracker(bot=bot))
