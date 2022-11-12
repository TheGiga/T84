import asyncio
import random
import uuid

import discord
import config
from discord.ext import tasks

from src import DefaultEmbed
from src.bot import T84
from src.models import User
from src.static import country_codes


class FlagEventButton(discord.ui.Button):
    def __init__(self, country_code: str):
        super().__init__()
        self.code: str = country_code
        self.custom_id = f'{country_code}.{uuid.uuid4()}'

        self.label = country_codes.get(self.code)
        self.style = discord.ButtonStyle.grey


class Events(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot
        self.flag_endpoint = 'https://flagcdn.com/h240/{}.png'
        self.codes: dict = country_codes

        self.channel_id = config.EVENT_CHANNEL_ID

        self.random_flag_event.start()

    @tasks.loop(minutes=30)
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
        embed.set_image(url=self.flag_endpoint.format(pick))

        view = discord.ui.View()

        place = random.randint(1, 4)

        for i in range(1, 5):  # Randomize button position
            if i == place:
                view.add_item(FlagEventButton(pick))
            else:
                fake = random.choice(picks)
                picks.remove(fake)
                view.add_item(FlagEventButton(fake))

        e_msg = await channel.send(embed=embed, view=view)

        def guess_check(interaction: discord.Interaction):
            # Splits custom id in half to get country code and checks if it's the one that was picked
            try:
                return interaction.data.get('custom_id').split('.')[0] == pick
            except AttributeError:
                return False

        try:
            guess: discord.Interaction = await self.bot.wait_for(
                "interaction", check=guess_check, timeout=60.0
            )
        except asyncio.TimeoutError:
            return await e_msg.delete()

        btn = view.children[place-1]
        btn.style = discord.ButtonStyle.green
        view.children[place-1] = btn

        view.disable_all_items()

        await e_msg.edit(
            content=f"**{guess.user.mention} відповів правильно!**",
            embed=e_msg.embeds[0].copy(),
            view=view
        )

        user, _ = await User.get_or_create(discord_id=guess.user.id)
        user.xp += config.FLAG_EVENT_XP_PRIZE
        await user.save()

        await guess.response.send_message(
            content=f'**Ви відповіли правильно!**\n'
                    f'Нагорода `{config.FLAG_EVENT_XP_PRIZE} XP`',
            ephemeral=True
        )


def setup(bot: T84):
    bot.add_cog(Events(bot=bot))
