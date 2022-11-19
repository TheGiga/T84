import discord
import config
from discord.ext import commands

from src.achievements import Achievements
from src.bot import T84
from src.models import User

achievements = [x.value.identifier for x in Achievements]


def admin_check(ctx: discord.ApplicationContext):
    return ctx.author.id in config.ADMINS


class AdminCommands(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    admin = discord.SlashCommandGroup('admin', "🛑 Адміністративні команди.")
    add_cmds = admin.create_subgroup('add', "➕")

    @add_cmds.command(name='balance', description='🛑 Добавити баланс.')
    @commands.check(admin_check)
    async def adm_add_balance(
            self, ctx: discord.ApplicationContext, amount: int,
            member: discord.Option(discord.Member), notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_balance(amount, notify_user=notify_user)

        await ctx.respond(content="☑ Успішно!", ephemeral=True)

    @add_cmds.command(name='achievement')
    @commands.check(admin_check)
    async def adm_add_achievement(
            self, ctx: discord.ApplicationContext, member: discord.Option(discord.Member),
            achievement: discord.Option(int, choices=achievements), notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_achievement(Achievements.get_from_id(achievement), notify_user=notify_user)

        await ctx.respond("☑ Успішно", ephemeral=True)


def setup(bot: T84):
    bot.add_cog(AdminCommands(bot=bot))
