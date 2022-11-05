import random
import discord
import config
from discord.ext import tasks

from src import DefaultEmbed
from src.models import User
from src.static import country_codes

user_cache: [int] = []


class FlagEventButton(discord.ui.Button):
    def __init__(self, country_code: str, primary=False):
        super().__init__()
        self.code: str = country_code
        self.primary = primary

        self.label = country_codes.get(self.code)
        self.style = discord.ButtonStyle.grey

    async def callback(self, interaction):
        if interaction.user.id in user_cache:
            return await interaction.response.send_message(
                content='❌ Ви вже відповідали на цей івент.', ephemeral=True
            )

        if not self.primary:
            user_cache.append(interaction.user.id)
            return await interaction.response.send_message(
                content='✖ Відповідь не вірна.', ephemeral=True
            )

        user_cache.append(interaction.user.id)

        self.style = discord.ButtonStyle.green
        self.view.disable_all_items()

        user, _ = await User.get_or_create(discord_id=interaction.user.id)
        user.xp += config.FLAG_EVENT_XP_PRIZE
        await user.save()

        await interaction.message.edit(view=self.view, embed=interaction.message.embeds[0].copy(), delete_after=30)

        await interaction.response.send_message(
            content=f'**{interaction.user.mention} відповів правильно!**\n'
                    f'Це був прапор: `{country_codes.get(self.code)}`\n\n'
                    f'||Нагорода `{config.FLAG_EVENT_XP_PRIZE} XP`||',
            delete_after=30
        )


class Events(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.flag_endpoint = 'https://flagcdn.com/h240/{}.png'
        self.codes: dict = country_codes

        self.channel_id = config.EVENT_CHANNEL_ID

        self.random_flag_event.start()

    @tasks.loop(minutes=random.randint(10, 30))
    async def random_flag_event(self):
        await self.bot.wait_until_ready()

        channel = await self.bot.fetch_channel(self.channel_id)

        picks: list = random.sample(
            list(self.codes.keys()), k=4
        )

        pick = picks[0]
        picks.pop(0)

        embed = DefaultEmbed()
        embed.title = "Що це за прапор?"
        embed.description = f"За правильну відповідь - нагорода `{config.FLAG_EVENT_XP_PRIZE} XP`"
        embed.colour.gold()
        embed.set_image(url=self.flag_endpoint.format(pick))

        view = discord.ui.View()

        place = random.randint(1, 4)

        for i in range(1, 5):
            if i == place:
                view.add_item(FlagEventButton(pick, True))
            else:
                fake = random.choice(picks)
                picks.remove(fake)
                view.add_item(FlagEventButton(fake, False))

        await channel.send(embed=embed, view=view, delete_after=240)


def setup(bot: discord.Bot):
    bot.add_cog(Events(bot=bot))
