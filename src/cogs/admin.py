import discord

import config
from src.achievements import Achievements, Achievement
from src.base_types import Unique
from src.bot import T84, T84ApplicationContext
from src.models import User

achievements = [
    discord.OptionChoice(x.value.key)
    for x in Achievements
]

changeable_roles = [
    discord.OptionChoice(str(x))
    for x in config.CHANGEABLE_ROLES
]

async def inventory_items(ctx: discord.AutocompleteContext):
    return [x for x in Unique.__instances__ if str(x).startswith(ctx.value) and str(x).endswith("_inv")]


class AdminCommands(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    admin = discord.SlashCommandGroup('admin', "🛑 Адміністративні команди.")
    add = admin.create_subgroup('add', "➕")

    def cog_check(self, ctx: discord.ApplicationContext):
        return ctx.author.id in self.bot.config.ADMINS

    @add.command(name='inventory_item')
    async def adm_add_inventory_item(
            self, ctx: T84ApplicationContext,
            member: discord.Option(discord.Member),
            item_key: discord.Option(str, name='item', autocomplete=inventory_items)
    ):
        user, _ = await User.get_or_create(discord_id=member.id)

        item = Unique.get_from_key(item_key)

        await user.add_inventory_item(item)

        await ctx.respond("☑️ Успішно.", ephemeral=True)

    @add.command(name='balance', description='🛑 Додати баланс.')
    async def adm_add_balance(
            self, ctx: T84ApplicationContext, member: discord.Option(discord.Member), amount: int,
            notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_balance(amount, notify_user=notify_user)

        await ctx.respond(content="☑️ Успішно!", ephemeral=True)

    @add.command(name='premium_balance', description='🛑 Додати преміум баланс.')
    async def adm_add_premium_balance(
            self, ctx: T84ApplicationContext, member: discord.Option(discord.Member),  amount: int,
            notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_premium_balance(amount, notify_user=notify_user)

        await ctx.respond(content="☑️ Успішно!", ephemeral=True)

    @add.command(name='stored_role', description='🛑 Додати перемикаєму роль.')
    async def adm_add_stored_role(
            self, ctx: T84ApplicationContext, member: discord.Member,
            role: discord.Option(str, choices=changeable_roles)
    ):
        user = await User.get(discord_id=member.id)

        await user.add_stored_role(int(role))

        await ctx.respond("☑️ Успішно", ephemeral=True)

    @add.command(name='achievement', description='🛑 Додати досягнення.')
    async def adm_add_achievement(
            self, ctx: T84ApplicationContext, member: discord.Member,
            achievement: discord.Option(str, choices=achievements), notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_achievement(Achievement.get_from_key(achievement), notify_user=notify_user)

        await ctx.respond("☑️ Успішно", ephemeral=True)


def setup(bot: T84):
    bot.add_cog(AdminCommands(bot=bot))
