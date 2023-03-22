import logging
import random

import discord
from discord.ext.commands import cooldown, BucketType

import src.static.assets
from src import T84ApplicationContext, DefaultEmbed
from src.bot import T84
from src.models import User

choices = ['копійка', 'володимир']
images = {
    'копійка': src.static.assets.RESHKA,
    'володимир': src.static.assets.OREL
}


class Gambling(discord.Cog):
    def __init__(self, bot):
        self.bot: T84 = bot

    #eco = discord.SlashCommandGroup(name='eco', description='🤑 Команди економіки та ігор.')

    @discord.slash_command(
        name='pay', description='💳 Перевести гроші іншому користувачу.'
    )
    @cooldown(1, 10, BucketType.user)
    async def eco_pay(
            self, ctx: T84ApplicationContext, member: discord.Option(discord.Member), amount: discord.Option(
                int, min_value=1, max_value=100_000
            )
    ):
        await ctx.defer(ephemeral=True)

        if ctx.user.id == member.id:
            return await ctx.respond("🤨 Реально? Сам собі?", ephemeral=True)

        front_user = ctx.user_instance
        end_user, _ = await User.get_or_create(discord_id=member.id)

        if amount > front_user.balance:
            return await ctx.respond('❌ Вам недостатньо коштів.', ephemeral=True)

        await front_user.add_balance(-amount)
        await end_user.add_balance(
            amount, notify_user=True, additional_message=f'*ℹ Трансфер від користувача {ctx.user.mention}*'
        )

        await ctx.respond(
            f'Ви успішно перевели **{amount}** 💸 користувачу {member.mention}. ', ephemeral=True
        )

        await self.bot.send_critical_log(
            f'{ctx.user.mention} `{front_user}` відіслав **{amount}** користувачу {member.mention} `{end_user}`',
            logging.INFO
        )

    # implement Player 2 Player coinflip system, instead of Player 2 Bot
    #@eco.command(
    #    name='coinflip',
    #    description='🃏 Коінфліп ігровою валютою. При виграші ви отримуєте +100% від ставки.'
    #)
    #@cooldown(1, 3, BucketType.user)
    async def eco_coinflip(
            self, ctx: T84ApplicationContext,
            amount: discord.Option(int, min_value=100, max_value=100_000),
            pick: discord.Option(str, choices=choices)
    ):
        user = ctx.user_instance

        if amount > user.balance:
            return await ctx.respond(
                f"❌ **Вам недостатньо коштів!**\n"
                f"*Доступний баланс: `{user.balance}`*",
                ephemeral=True
            )

        bot_choice = random.choice(choices)

        embed = DefaultEmbed()

        if bot_choice != pick:
            embed.title = 'Ви програли, всі ваші гроші тепер мої! 😎'
            embed.description = f"**-{amount}** 💸"
            embed.set_thumbnail(url=images.get(bot_choice))

            await ctx.respond(embed=embed)
            return

        await user.add_balance(amount)

        embed.title = 'Ви виграли 😢'
        embed.description = f"**+{amount}** 💸"
        embed.set_thumbnail(url=images.get(bot_choice))

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Gambling(bot))
