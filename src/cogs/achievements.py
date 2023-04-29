import discord
from src import DefaultEmbed
from src.bot import T84, T84ApplicationContext
from src.achievements import Achievement, Achievements as AchievementsEnum
from src.models import User

viewable_achievements = [
    discord.OptionChoice(x.value.name, x.value.key)
    for x in AchievementsEnum
    if not x.value.secret
]


class Achievements(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @discord.slash_command(name='achievements', description='⭐ Подивитися інформацію про досягнення користувача.')
    async def achievements(
            self, ctx: T84ApplicationContext,
            discord_instance: discord.Option(discord.Member, name='member', description="Користувач.") = None
    ):
        discord_instance = discord_instance or ctx.author

        await ctx.defer()

        user, _ = await User.get_or_create(discord_id=discord_instance.id)

        embed = DefaultEmbed()
        embed.title = f"Досягнення користувача {discord_instance.display_name}"
        embed.set_thumbnail(url=discord_instance.display_avatar.url)

        achievements = ""

        for ach in user.achievements:
            achievements += f"☑️ {ach.name}\n"

        embed.description = f"""
        Кількість досягнень: `{len(user.achievements)}/{len(AchievementsEnum)}`
        
        {achievements}
        """

        await ctx.respond(embed=embed)

    @discord.slash_command(name='achievement', description='⭐ Подивитися інформацію про досягнення.')
    async def achievement(
            self, ctx: T84ApplicationContext, achievement_key: discord.Option(
                str, choices=viewable_achievements, name='achievement',
                description="Тут можна подивитися інформацію про незасекречені досягнення."
            )
    ):
        achievement: Achievement | None = Achievement.get_from_key(achievement_key)

        if achievement is None:
            return await ctx.respond(content="❌ Досягнення з таким номером не знайдено!", ephemeral=True)

        await ctx.user_instance.add_achievement(Achievement.get_from_key("ach_interested"), notify_user=True)

        embed = DefaultEmbed()
        embed.colour = discord.Colour.dark_blue()

        embed.title = achievement.name

        embed.description = achievement.description

        await ctx.respond(embed=embed)

    @discord.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member | discord.User):
        if not hasattr(user, "guild"):
            return

        if user.guild.id != self.bot.config.PARENT_GUILD:
            return

        match reaction.emoji:
            case "🍉":
                user, _ = await User.get_or_create(discord_id=user.id)
                await user.add_achievement(Achievement.get_from_key("ach_watermelon"), notify_user=True)

            case "💣":
                user, _ = await User.get_or_create(discord_id=user.id)
                await user.add_achievement(Achievement.get_from_key("ach_donbass"), notify_user=True)

            case "💀":
                user, _ = await User.get_or_create(discord_id=user.id)
                await user.add_achievement(Achievement.get_from_key("ach_skull"), notify_user=True)


def setup(bot: T84):
    bot.add_cog(Achievements(bot=bot))
