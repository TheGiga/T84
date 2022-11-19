import discord
import config
from discord.ext import commands
from src.bot import T84
from src.models import User


def admin_check(ctx: discord.ApplicationContext):
    return ctx.author.id in config.ADMINS


class AdminCommands(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    admin = discord.SlashCommandGroup('admin', "🛑 Адміністративні команди.")

    @admin.command(name='add_balance', description='🛑 Добавити баланс.')
    @commands.check(admin_check)
    async def adm_add_balance(
            self, ctx: discord.ApplicationContext, amount: int,
            member: discord.Option(discord.Member), notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_balance(amount, notify_user=notify_user)

        await ctx.respond(content="☑ Успішно!", ephemeral=True)


def setup(bot: T84):
    bot.add_cog(AdminCommands(bot=bot))
