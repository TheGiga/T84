import discord
from discord import guild_only

from src import DefaultEmbed
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

        user = await User.get(discord_id=member.id)

        embed = DefaultEmbed()
        embed.title = f"**Профіль користувача {member.display_name}**"

        embed.add_field(name='⚖ Рівень', value=f'`{user.level}`')
        embed.add_field(name='🔢 UID', value=f'`#{user.id}`')
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Profile(bot))
