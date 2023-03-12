import discord
from src.bot import T84, T84ApplicationContext
from pycord.multicog import add_to_group
from .. import DefaultEmbed


class SelfRoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role, row: int):
        super().__init__(
            label=role.name,
            style=discord.ButtonStyle.green,
            custom_id=str(role.id),
            row=row
        )

    async def callback(self, interaction: discord.Interaction):
        new_interaction = await interaction.response.send_message(content='🔃 У процесі...', ephemeral=True)

        user = interaction.user
        role = interaction.guild.get_role(int(self.custom_id))

        original_response = await new_interaction.original_response()

        if role is None:
            await original_response.edit("❌ Сталася помилка :(")
            return

        if role not in user.roles:
            await user.add_roles(role)
            await original_response.edit(
                f"☑ Вам було успішно видано роль {role.mention}!",
            )
        else:
            await user.remove_roles(role)
            await original_response.edit(
                f"❌ Роль {role.mention} було успішно забрано у вас.",
            )


class InteractiveViews(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    def cog_check(self, ctx: discord.ApplicationContext):
        return ctx.author.id in self.bot.config.ADMINS

    # TODO: Make this command universal
    @add_to_group("admin")
    @discord.slash_command(name='post_self_roles', description='🛑 Administrative control on interactive views.')
    async def adm_post_view(
            self, ctx: T84ApplicationContext
    ):
        guild = await self.bot.parent_guild
        channel = guild.get_channel(self.bot.config.SELF_ROLES_CHANNEL_ID)

        view = discord.ui.View(timeout=None)
        embed = DefaultEmbed()
        embed.title = '🎯 Авто-ролі'

        for i, role_id in enumerate(self.bot.config.SELF_ROLES_IDS, start=1):
            row = (i - 1) // 3

            role = guild.get_role(role_id)
            view.add_item(SelfRoleButton(role, row=row))

        await channel.send(view=view, embed=embed)

        await ctx.respond('☑ Успішно', ephemeral=True)

    @discord.Cog.listener()
    async def on_ready(self):

        # Self Roles V

        view = discord.ui.View(timeout=None)

        guild = await self.bot.parent_guild

        for i, role_id in enumerate(self.bot.config.SELF_ROLES_IDS, start=1):
            row = (i - 1) // 3

            role = guild.get_role(role_id)
            view.add_item(SelfRoleButton(role, row=row))

        self.bot.add_view(view)

        # Self Roles END ^


def setup(bot: T84):
    bot.add_cog(InteractiveViews(bot))
