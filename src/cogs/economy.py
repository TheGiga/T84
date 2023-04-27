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
    async def pay(
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

    @discord.slash_command(name='work', description='💰 Невелика кількість валюти раз в день.')
    @cooldown(1, 43200, BucketType.user)
    async def work(self, ctx: T84ApplicationContext):
        money = random.randint(self.bot.config.WORK_MIN_AMOUNT, self.bot.config.WORK_MAX_AMOUNT)
        await ctx.user_instance.add_balance(money)

        embed = DefaultEmbed()
        embed.title = "💰 Праця"
        embed.description = f"Ваша зарплатня за цей день: `{money} 💸`"
        embed.colour = discord.Colour.green()

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Gambling(bot))
