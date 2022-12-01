import discord

from src.bot import T84
from src.models import User


class Profile(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @discord.slash_command(name='profile', description='👤 Перевірка профілю юзера.')
    async def profile(
            self, ctx: discord.ApplicationContext,
            member: discord.Option(discord.Member, description="👤 Юзер") = None
    ):
        if member is None:
            member = ctx.author

        user, _ = await User.get_or_create(discord_id=member.id)

        embed = await user.get_profile_embed()

        await ctx.respond(embed=embed)

    @discord.slash_command(name='balance', description='👤 Перевірити свій баланс.')
    async def balance(self, ctx: discord.ApplicationContext):
        user = await User.get(discord_id=ctx.author.id)

        await user.add_achievement(2013, notify_user=True)

        await ctx.respond(f"Ваш баланс: **{user.balance}** 💸", ephemeral=True)


def setup(bot: T84):
    bot.add_cog(Profile(bot))
