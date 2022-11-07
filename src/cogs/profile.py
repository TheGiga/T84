import discord
from discord import guild_only
from src.models import User


class Profile(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @guild_only()
    @discord.slash_command(
        name='profile',
        description='👤 Перевірка профілю юзера.'
    )
    async def profile(
            self, ctx: discord.ApplicationContext,
            member: discord.Option(discord.Member, description="👤 Юзер") = None
    ):
        if member is None:
            member = ctx.author

        user, _ = await User.get_or_create(discord_id=member.id)

        embed = await user.get_profile_embed()

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Profile(bot))
