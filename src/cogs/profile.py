import discord
from discord import guild_only
from src import DefaultEmbed
from src.models import User


def progress_bar(percent: int) -> str:
    raw_percents = percent // 10
    bar = ""

    for _ in range(raw_percents):
        bar += "⬛"

    final = bar.ljust(10, "🟨")
    return final[::-1]


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

        await user.get_discord_instance(guild=ctx.guild)

        embed = DefaultEmbed()
        embed.title = f"**Профіль користувача {member.display_name}**"

        embed.add_field(name='⚖ Рівень', value=f'`{user.level}`')
        embed.add_field(name='🎈 Досвід', value=f'`{user.xp}`')
        embed.add_field(name='🔢 UID', value=f'`#{user.id}`')
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.description = f"""
        Прогрес до слідуючого рівню: `{user.xp}/{user.level_to_xp(user.level+1)}`
        > ```{progress_bar(user.xp_tnl_percent)}```
        """

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Profile(bot))
