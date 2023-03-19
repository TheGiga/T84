import discord
from discord import HTTPException

from src.achievements import Achievements, Achievement
from src.base_types import Unique
from src.bot import T84, T84ApplicationContext
from src.models import User
from src.rewards import leveled_rewards

achievements = [
    discord.OptionChoice(x.value.name, x.value.uid)
    for x in Achievements
]

async def inventory_items(ctx: discord.AutocompleteContext):
    return [discord.OptionChoice(x.name) for x in Unique.__instances__ if str(x).startswith(ctx.value)]


class AdminCommands(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    admin = discord.SlashCommandGroup('admin', "🛑 Адміністративні команди.")

    mass_role = admin.create_subgroup('mass-role', "✅ ❌")
    add = admin.create_subgroup('add', "➕")
    recalculate = admin.create_subgroup("recalculate", "♻")

    def cog_check(self, ctx: discord.ApplicationContext):
        return ctx.author.id in self.bot.config.ADMINS

    @mass_role.command(name='add', description='✅ Add role to all guild members.')
    async def mass_role_add(self, ctx: T84ApplicationContext, role: discord.Option(discord.Role)):

        await ctx.respond(content='Processing...', ephemeral=True)

        cases = 0
        failed = ''

        for member in ctx.guild.members:
            try:
                await member.add_roles(role, reason=f"Mass-role addition by {ctx.author}")
                cases += 1
            except HTTPException:
                failed += f'{member.mention} '

        await ctx.send_followup(content=f'✅ Done! `({cases})`\n', ephemeral=True)

        if len(failed) > 0:
            await ctx.send_followup(content=f'Fails: {str(failed)}', ephemeral=True)

    @mass_role.command(name='remove', description="❌ Remove role from all it's members.")
    async def mass_role_add(self, ctx: T84ApplicationContext, role: discord.Option(discord.Role)):

        await ctx.respond(content='Processing...', ephemeral=True)

        cases = 0
        failed = ''

        for member in role.members:
            try:
                await member.remove_roles(role, reason=f"Mass-role removal by {ctx.author}")
                cases += 1
            except HTTPException:
                failed += f'{member.mention} '

        await ctx.send_followup(content=f'✅ Done! `({cases})`\n', ephemeral=True)

        if len(failed) > 0:
            await ctx.send_followup(content=f'Fails: {str(failed)}', ephemeral=True)

    @add.command(name='inventory_item')
    async def adm_add_inventory_item(
            self, ctx: T84ApplicationContext,
            item_id: discord.Option(int, name='item', autocomplete=inventory_items),
            member: discord.Option(discord.Member)
    ):
        user, _ = await User.get_or_create(discord_id=member.id)

        item = Unique.get_from_id(item_id)

        await user.add_inventory_item(item)

        await ctx.respond("☑ Успішно.", ephemeral=True)

    @recalculate.command(name='rewards', description='♻')
    async def adm_recalculate_rewards(
            self, ctx: T84ApplicationContext, member: discord.Member,
            reward_type: discord.Option(name='type', choices=['role', 'achievement', 'balance'])
    ):
        user, _ = await User.get_or_create(discord_id=member.id)

        await ctx.defer(ephemeral=True)

        overall_applied_rewards = []

        for reward_level in leveled_rewards:
            if reward_level > user.level:
                break

            rewards_raw = leveled_rewards.get(reward_level)
            rewards_to_apply = tuple(x for x in rewards_raw if x.code == reward_type)

            overall_applied_rewards.extend(rewards_to_apply)

            await user.apply_rewards(rewards_to_apply)

        content = f"☑ Успішно, видані нагороди: ```py\n{overall_applied_rewards}```"

        if reward_type == "balance":
            content += f'\n\nУсього: `{sum(x.payload for x in overall_applied_rewards)}` 💸'

        await ctx.respond(content, ephemeral=True)

    @add.command(name='balance', description='🛑 Додати баланс.')
    async def adm_add_balance(
            self, ctx: T84ApplicationContext, amount: int,
            member: discord.Option(discord.Member), notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_balance(amount, notify_user=notify_user)

        await ctx.respond(content="☑ Успішно!", ephemeral=True)

    @add.command(name='premium_balance', description='🛑 Додати преміум баланс.')
    async def adm_add_premium_balance(
            self, ctx: T84ApplicationContext, amount: int,
            member: discord.Option(discord.Member), notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_premium_balance(amount, notify_user=notify_user)

        await ctx.respond(content="☑ Успішно!", ephemeral=True)

    @add.command(name='achievement', description='🛑 Добавити досягнення.')
    async def adm_add_achievement(
            self, ctx: T84ApplicationContext, member: discord.Option(discord.Member),
            achievement: discord.Option(int, choices=achievements), notify_user: bool = False
    ):
        user = await User.get(discord_id=member.id)

        await user.add_achievement(Achievement.get_from_id(achievement), notify_user=notify_user)

        await ctx.respond("☑ Успішно", ephemeral=True)


def setup(bot: T84):
    bot.add_cog(AdminCommands(bot=bot))
