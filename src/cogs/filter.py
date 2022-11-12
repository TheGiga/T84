import discord
import config
from src.bot import T84


class Filter(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @discord.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return

        if not payload.emoji.is_unicode_emoji():
            return

        if payload.emoji.__str__() in config.BLACKLIST:
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel_or_thread(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            await message.clear_reaction(emoji=payload.emoji)

            try:
                await payload.member.send(f"❌ Добавление реакции {payload.emoji} запрещено на сервере!")
            except discord.HTTPException:
                pass


def setup(bot: T84):
    bot.add_cog(Filter(bot=bot))
