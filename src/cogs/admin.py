import discord
import config
from discord.ext import commands

from src.achievements import Achievements
from src.bot import T84
from src.models import User
from src.rewards import leveled_rewards

achievements = [x.value.identifier for x in Achievements]


def admin_check(ctx: discord.ApplicationContext):
    return ctx.author.id in config.ADMINS


class AdminCommands(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    admin = discord.SlashCommandGroup('admin', "🛑 Адміністративні команди.")
    add = admin.create_subgroup('add', "➕")
    recalculate = admin.create_subgroup("recalculate", "♻")

    @recalculate.command(name='rewards', description='♻')
    @commands.check(admin_check)
    async def adm_recalculate_rewards(
            self, ctx: discord.ApplicationContext, member: discord.Member,
            reward_type: discord.Option(name='type', choices=['role', 'achievement', 'balance'])
    ):
        user, _ = await User.get_or_create(discord_id=member.id)

        await ctx.defer()

        overall_applied_rewards = []

        for reward_level in leveled_rewards:
            if reward_level > user.level:
                break

            rewards_raw = leveled_rewards.get(reward_level)
            rewards_to_apply = tuple(x for x in rewards_raw if x.value.code == reward_type)

            overall_applied_rewards.extend(rewards_to_apply)

            await user.apply_rewards(rewards_to_apply)

        content = f"☑ Успішно, видані нагороди: ```py\n{overall_applied_rewards}```"

        if reward_type == "balance":
            content += f'\n\nУсього: `{sum(x.value.payload for x in overall_applied_rewards)}` 💸'

        await ctx.respond(content, ephemeral=True)

    @add.command(name='balance', description='🛑 Добавити баланс.')
    @commands.check(admin_check)
    async def adm_add_balance(
            self, ctx: discord.ApplicationContext, amount: int,
            member: discord.Option(discord.Member), notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_balance(amount, notify_user=notify_user)

        await ctx.respond(content="☑ Успішно!", ephemeral=True)

    @add.command(name='achievement', description='🛑 Добавити досягнення.')
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
