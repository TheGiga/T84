import discord
from typing import Union

from src import DefaultEmbed
from src.bot import T84
from src.achievements import Achievement, Achievements as AchievementsEnum, MsgCountAchievement
from src.models import User


class Achievements(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @discord.slash_command(name='achievements', description='⭐ Подивитися інформацію про досягнення користувача.')
    async def achievements(
            self, ctx: discord.ApplicationContext,
            discord_instance: discord.Option(discord.Member, name='member', description="Користувач.") = None
    ):
        discord_instance = discord_instance or ctx.author

        await ctx.defer()

        user = await User.get(discord_id=discord_instance.id)

        embed = DefaultEmbed()
        embed.title = f"Досягнення користувача {discord_instance.display_name}"
        embed.set_thumbnail(url=discord_instance.display_avatar.url)

        msg_achievement: MsgCountAchievement | None = None

        other_achievements = ""

        for ach in user.achievements:
            ach_object = Achievement.get_from_id(ach)
            if type(ach_object) is MsgCountAchievement:
                msg_achievement = ach_object

            else:
                other_achievements += f"☑️ {ach_object.name} `({ach_object.fake_id})`\n"

        if msg_achievement is not None:
            embed.add_field(name=f'{msg_achievement.name}', value=f'{msg_achievement.description}')

        embed.description = f"""
        Кількість досягнень: `{len(user.achievements)}/{len(AchievementsEnum)}`
        
        {other_achievements}
        ──────────────────────────
        """

        await ctx.respond(embed=embed)
        # await user.add_achievement(achievement=AchievementsEnum.get_from_id(8), notify_user=True)

    @discord.slash_command(name='achievement', description='⭐ Подивитися інформацію про досягнення.')
    async def achievement(
            self, ctx: discord.ApplicationContext, identifier: discord.Option(
                int, name='id', description="Номер досягнення. Усі досягнення пронумеровані по порядку.",
                min_value=1, max_value=len(AchievementsEnum)
            )
    ):
        # +2000 because I use fake achievement ID's on frontend, so people can easily manage them.
        # 1, 2, 3 is better than 2001, 2002, 2003... right?
        achievement: Union[Achievement, None] = Achievement.get_from_id(identifier+2000)

        if achievement is None:
            return await ctx.respond(content="❌ Досягнення з таким номером не знайдено!", ephemeral=True)

        if achievement is Achievement.get_from_id(2011):
            user = await User.get(discord_id=ctx.author.id)
            await user.add_achievement(2011, notify_user=True)

        if achievement.secret:
            embed = DefaultEmbed()
            embed.title = "???"
            embed.description = "*Це досягнення засекречене!*"
            embed.colour = discord.Colour.red()

            return await ctx.respond(embed=embed)

        embed = DefaultEmbed()
        embed.colour = discord.Colour.blurple()

        embed.title = achievement.name

        embed.description = achievement.description

        await ctx.respond(embed=embed)

    @discord.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member | discord.User):
        if not hasattr(user, "guild"):
            return

        if user.guild.id != self.bot.config.PARENT_GUILD:
            return

        if reaction.emoji == "🍉":
            user, _ = await User.get_or_create(discord_id=user.id)
            await user.add_achievement(Achievement.get_from_id(2009), notify_user=True)

        elif reaction.emoji == "💣":
            user, _ = await User.get_or_create(discord_id=user.id)
            await user.add_achievement(Achievement.get_from_id(2014), notify_user=True)


def setup(bot: T84):
    bot.add_cog(Achievements(bot=bot))
