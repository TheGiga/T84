import discord
from discord import guild_only
from src import DefaultEmbed
from src.models import User


def progress_bar(percent: int) -> str:
    raw_percents = percent // 10
    bar = ""

    for _ in range(raw_percents):
        bar += "🟨"

    final = bar.ljust(10, "⬛")
    return final


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

        await user.get_discord_instance(guild=ctx.guild)

        embed = DefaultEmbed()
        embed.title = f"**Профіль користувача {member.display_name}**"

        embed.add_field(name='⚖ Рівень', value=f'`{user.level}`')
        embed.add_field(name='🎈 Досвід', value=f'`{user.xp}`')
        embed.add_field(name='🔢 UID', value=f'`#{user.id}`')
        embed.set_thumbnail(url=member.display_avatar.url)

        xp_new_level_full = user.level_to_xp(user.level + 1)
        xp_current_level = user.level_to_xp(user.level)
        xp_to_new_level = user.xp - xp_current_level
        xp_new_level = xp_new_level_full - xp_current_level

        percent = round((xp_to_new_level / xp_new_level) * 100)

        embed.description = f"""
        Прогрес до наступного рівню: `{user.xp}/{user.level_to_xp(user.level+1)}`
        > ```{user.level} {progress_bar(percent)} {user.level+1}```
        """

        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Profile(bot))
