import datetime

import discord
import calendar
from discord.ext import tasks
from discord.ext.commands import cooldown, BucketType
from discord import ButtonStyle
from math import floor

from tortoise.exceptions import IntegrityError

from src import DefaultEmbed
from src.bot import T84, T84ApplicationContext
from src.models import XPBooster, User

boosters = [ # (multiplier, duration in minutes, price)
    (2.00, 30, 2000),
    (1.50, 60, 2000),
    (1.25, 120, 2000)
]

class MultiplierButton(discord.ui.Button):
    def __init__(self, multiplier: float, duration: int, price: int, curr_row: int):
        self.multiplier = multiplier
        self.duration = duration
        self.price = price
        super().__init__(
            label=f"{price} 💸 | {multiplier}x | {duration} хв",
            style=ButtonStyle.green,
            row=curr_row
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.init_user.id:
            return await interaction.response.send_message(
                "❌ Пропишіть `/booster buy` щоб купувати бустер.", ephemeral=True
            )

        user, _ = await User.get_or_create(discord_id=interaction.user.id)

        if user.balance < self.price:
            return await interaction.response.send_message(
                "❌ У вас недостатньо коштів!", ephemeral=True)

        try:
            booster = await XPBooster.create(
                user_id=user.id,
                valid_until=datetime.datetime.utcnow() + datetime.timedelta(minutes=self.duration),
                power=self.multiplier
            )

            await user.add_balance(-self.price)
            await booster.apply()

            await interaction.response.send_message(
                content=f"✅ Ви успішно придбали бустер!\n\n"
                        f"- Закінчується: <t:{calendar.timegm(booster.valid_until.utctimetuple())}:R>\n"
                        f"- Сила: `{booster.power}x`",
                ephemeral=True
            )

            self.view.disable_all_items()
            await interaction.message.edit(view=self.view)


        except IntegrityError:
            active_booster = await XPBooster.get(user_id=user.id)
            return await interaction.response.send_message(
                content=f"❌ У вас вже є активний бустер.\n\n"
                        f"- Закінчується: <t:{calendar.timegm(active_booster.valid_until.utctimetuple())}:R>\n"
                        f"- Сила: `{active_booster.power}x`",
                ephemeral=True
            )

class Boosters(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot
        self.booster_cleaner.start()

    booster_group = discord.SlashCommandGroup(name='booster', description="⬆️ Серверні бустери XP")

    @cooldown(1, 30, BucketType.user)
    @booster_group.command(name='buy', description='⬆️ Придбання бустерів XP')
    async def booster_buy(self, ctx: T84ApplicationContext):
        embed = DefaultEmbed()
        embed.title = "⚗️ Бустери XP"
        embed.description = """
        Ви можете купувати тимчасові бустери XP тут.
        
        *⚠️ Ви можете купувати лише один бустер за раз!*
        """

        view = discord.ui.View()
        view.init_user = ctx.user

        curr_row = 1

        for multiplier, duration, price in boosters:
            button = MultiplierButton(
                multiplier, duration, price, curr_row=floor(curr_row)
            )

            view.add_item(button)
            curr_row += 0.5

        await ctx.respond(embed=embed, view=view)

    @booster_group.command(name='active', description='⬆️ Подивитися інформацію про активний бустер.')
    async def booster_active(self, ctx: T84ApplicationContext):
        active_booster = await XPBooster.get_or_none(user_id=ctx.user_instance.id)

        if active_booster is None:
            return await ctx.respond('❌ У вас немає активного бустеру.\n- Пропишіть `/booster buy` для придбання.')

        await ctx.respond(
            content=f"⬆️ Активний бустер:\n\n"
                    f"- Закінчується: <t:{calendar.timegm(active_booster.valid_until.utctimetuple())}:R>\n"
                    f"- Сила: `{active_booster.power}x`",
            ephemeral=True
        )

    @tasks.loop(seconds=30)
    async def booster_cleaner(self):
        await self.bot.wait_until_ready()
        await XPBooster.delete_all_expired()


def setup(bot: T84):
    bot.add_cog(Boosters(bot))