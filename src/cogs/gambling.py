import logging
import random

import discord
from discord.ext.commands import cooldown, BucketType

import src.static.assets
from src import T84ApplicationContext, DefaultEmbed
from src.bot import T84
from src.models import User, Bank

choices = ['копійка', 'володимир']
images = {
    'копійка': src.static.assets.RESHKA,
    'володимир': src.static.assets.OREL
}


class Gambling(discord.Cog):
    def __init__(self, bot):
        self.bot: T84 = bot

    eco = discord.SlashCommandGroup(name='eco', description='🤑 Команди економіки та ігор.')

    @discord.slash_command(name='bank', description='🏦 Перевірити баланси банку.')
    async def check_bank(self, ctx: T84ApplicationContext):
        bank = await Bank.get(id=1)

        embed = DefaultEmbed()
        embed.colour = discord.Colour.green()
        embed.title = "🏦 Банк"

        embed.description = f'У банку на даний момент знаходитися **{bank.balance}** 💸 для вільних виплат.\n\n' \
                            f'*ℹ Усі податки з любих операцій з валютою та програші в різноманітних іграх поповніють ' \
                            f'цей банк, також ця валюта забезпечує виплату виграшу у любій з ігор.*'

        await ctx.respond(embed=embed)

    @discord.slash_command(
        name='pay', description='💳 Перевести гроші іншому користувачу. (Комісія 10%)'
    )
    @cooldown(1, 20, BucketType.user)
    async def eco_pay(
            self, ctx: T84ApplicationContext, member: discord.Option(discord.Member), amount: discord.Option(
                int, min_value=10, max_value=100_000
            )
    ):
        await ctx.defer(ephemeral=True)

        if ctx.user.id == member.id:
            return await ctx.respond("🤨 Реально? Сам собі?", ephemeral=True)

        front_user = ctx.user_instance
        end_user, _ = await User.get_or_create(discord_id=member.id)

        if amount > front_user.balance:
            return await ctx.respond('❌ Вам недостатньо коштів.', ephemeral=True)

        amount_after_tax = round(amount * 0.90)

        bank = await Bank.get(id=1)
        await bank.add(round(amount * 0.1))

        await front_user.add_balance(-amount)
        await end_user.add_balance(
            amount_after_tax, notify_user=True, additional_message=f'*ℹ Трансфер від користувача {ctx.user.mention}*'
        )

        await ctx.respond(
            f'Ви успішно перевели **{amount}** 💸 користувачу {member.mention}. '
            f'||{amount_after_tax} 💸 після комісії||', ephemeral=True
        )

        await self.bot.send_critical_log(
            f'{ctx.user.mention} `{front_user}` відіслав **{amount}** користувачу {member.mention} `{end_user}`',
            logging.INFO
        )

    @eco.command(
        name='coinflip',
        description='🃏 Коінфліп ігровою валютою. При виграші ви отримуєте +99% від ставки (1% я вкрав)'
    )
    @cooldown(1, 3, BucketType.user)
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

        bank = await Bank.get(id=1)

        if round(amount * 0.99) > bank.balance:
            return await ctx.respond(
                "❌ У **🏦 Банку** недостатньо коштів щоб покрити можливий виграш.\n"
                "- *Ви можете перевірити баланс банку командою `/bank`.",
                ephemeral=True
            )

        bot_choice = random.choice(choices)

        embed = DefaultEmbed()

        if bot_choice != pick:
            await user.add_balance(-amount)
            await bank.add(amount)

            embed.title = 'Ви програли, всі ваші гроші тепер мої! 😎'
            embed.description = f"**-{amount}** 💸"
            embed.set_thumbnail(url=images.get(bot_choice))

            await ctx.respond(embed=embed)
            return

        win_amount = round(amount * 0.99)

        await bank.withdraw(win_amount)

        await user.add_balance(win_amount)

        embed.title = 'Ви виграли 😢'
        embed.description = f"**+{win_amount}** 💸"
        embed.set_thumbnail(url=images.get(bot_choice))

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Gambling(bot))
