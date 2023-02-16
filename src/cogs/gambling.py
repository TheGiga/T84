import random

import discord
from discord.ext.commands import cooldown, BucketType

import src.static.assets
from src import T84ApplicationContext, DefaultEmbed

choices = ['копійка', 'володимир']
images = {
    'копійка': src.static.assets.RESHKA,
    'володимир': src.static.assets.OREL
}


class Gambling(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    eco = discord.SlashCommandGroup(name='eco', description='🤑 Команди економіки та ігор.')

    @eco.command(
        name='coinflip',
        description='🃏 Коінфліп ігровою валютою. При виграші ви отримуєте +95% від ставки (5% я вкрав)'
    )
    @cooldown(1, 3, BucketType.user)
    async def eco_coinflip(
            self, ctx: T84ApplicationContext,
            amount: discord.Option(int, min_value=1, max_value=1_000_000),
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
            await user.add_balance(-amount)

            embed.title = 'Ви програли, всі ваші гроші тепер мої! 😎'
            embed.description = f"**-{amount}** 💸"
            embed.set_thumbnail(url=images.get(bot_choice))

            await ctx.respond(embed=embed)
            return

        win_amount = round(amount * 0.95)

        await user.add_balance(win_amount)

        embed.title = 'Ви виграли 😢'
        embed.description = f"**+{win_amount}** 💸"
        embed.set_thumbnail(url=images.get(bot_choice))

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Gambling(bot))
