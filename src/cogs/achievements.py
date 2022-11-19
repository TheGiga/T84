import discord
from typing import Union

import config
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
        if discord_instance is None:
            discord_instance = ctx.author

        await ctx.defer()

        user = await User.get(discord_id=discord_instance.id)

        embed = DefaultEmbed()
        embed.title = f"Досягнення користувача {discord_instance.display_name}"
        embed.set_thumbnail(url=discord_instance.display_avatar.url)

        msg_achievement: MsgCountAchievement | None = None

        other_achievements = ""

        for ach in user.achievements:
            ach_object = AchievementsEnum.get_from_id(ach)
            if type(ach_object) is MsgCountAchievement:
                msg_achievement = ach_object

            else:
                other_achievements += f"☑️ {ach_object.text} `({ach_object.identifier})`\n"

        if msg_achievement is not None:
            embed.add_field(name=f'{msg_achievement.text}', value=f'{msg_achievement.long_text}')

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
                int, name='id', description="Номер досягнення. Усі досягнення пронумеровані по порядку."
            )
    ):
        achievement: Union[Achievement, None] = AchievementsEnum.get_from_id(identifier)

        if achievement is None:
            return await ctx.respond(content="❌ Досягнення з таким номером не знайдено!", ephemeral=True)

        if achievement.secret:
            embed = DefaultEmbed()
            embed.title = f"{achievement.text}"
            embed.description = "*Це досягнення засекречене!*"

            return await ctx.respond(embed=embed)

        embed = DefaultEmbed()
        embed.colour = discord.Colour.blurple()

        embed.title = achievement.text
        embed.description = achievement.long_text

        await ctx.respond(embed=embed)

    @discord.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member | discord.User):
        if not hasattr(user, "guild"):
            return

        if user.guild.id != config.PARENT_GUILD:
            return

        if reaction.emoji == "🍉":
            user, _ = await User.get_or_create(discord_id=user.id)
            await user.add_achievement(AchievementsEnum.get_from_id(9), notify_user=True)


def setup(bot: T84):
    bot.add_cog(Achievements(bot=bot))
