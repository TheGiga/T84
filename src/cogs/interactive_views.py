import discord
from discord.ext import commands

from src.bot import T84, T84ApplicationContext
from pycord.multicog import add_to_group
from .admin import admin_check
from .. import DefaultEmbed


class SelfRoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role):
        super().__init__(
            label=role.name,
            style=discord.ButtonStyle.green,
            custom_id=str(role.id),
        )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        role = interaction.guild.get_role(int(self.custom_id))

        if role is None:
            return

        if role not in user.roles:
            await user.add_roles(role)
            await interaction.response.send_message(
                f"☑ Вам було успішно видано роль {role.mention}!",
                ephemeral=True,
            )
        else:
            await user.remove_roles(role)
            await interaction.response.send_message(
                f"❌ Роль {role.mention} було успішно забрано у вас.",
                ephemeral=True,
            )


class InteractiveViews(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    # TODO: Make this command universal
    @add_to_group("admin")
    @commands.check(admin_check)
    @discord.slash_command(name='post_self_roles', description='🛑 Administrative control on interactive views.')
    async def adm_post_view(
            self, ctx: T84ApplicationContext
    ):
        guild = await self.bot.parent_guild
        channel = guild.get_channel(self.bot.config.SELF_ROLES_CHANNEL_ID)

        view = discord.ui.View(timeout=None)
        embed = DefaultEmbed()
        embed.title = '🎯 Ролі режимів'

        for role_id in self.bot.config.SELF_ROLES_IDS:
            role = guild.get_role(role_id)
            view.add_item(SelfRoleButton(role))

        await channel.send(view=view, embed=embed)

        await ctx.respond('☑ Успішно', ephemeral=True)

    @discord.Cog.listener()
    async def on_ready(self):

        # Self Roles V

        view = discord.ui.View(timeout=None)

        guild = await self.bot.parent_guild

        for role_id in self.bot.config.SELF_ROLES_IDS:
            role = guild.get_role(role_id)
            view.add_item(SelfRoleButton(role))

        self.bot.add_view(view)

        # Self Roles END ^


def setup(bot: T84):
    bot.add_cog(InteractiveViews(bot))
