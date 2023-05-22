import discord
from discord import Interaction, ButtonStyle
from discord.ext.commands import cooldown, BucketType
from numpy import setdiff1d

from src import T84ApplicationContext, DefaultEmbed
from src.achievements import Achievement
from src.bot import T84
from src.models import User

corr_vals = {
    True: ButtonStyle.green,
    False: ButtonStyle.red
}

class ToggleRole(discord.ui.Button):
    def __init__(self, role: discord.Role, initial_state: bool):
        super().__init__()
        self.role = role
        self.state = initial_state
        self.label = role.name

        if self.role.unicode_emoji:
            self.emoji = self.role.unicode_emoji

        self.style = corr_vals[initial_state]

    async def callback(self, interaction: Interaction):
        if self.state:
            await interaction.user.remove_roles(self.role)
        else:
            await interaction.user.add_roles(self.role)

        self.state = not self.state
        self.style = corr_vals[self.state]

        await interaction.response.edit_message(view=self.view)

class Profile(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @discord.slash_command(name='profile', description='👤 Переглянути профіль користувача.')
    async def profile(
            self, ctx: T84ApplicationContext,
            member: discord.Option(discord.Member, description="👤 Юзер") = None
    ):
        await ctx.defer()

        member = member or ctx.author

        user, _ = await User.get_or_create(discord_id=member.id)

        embed = await user.get_profile_embed()

        await ctx.respond(embed=embed)

    @discord.slash_command(name='balance', description='👤 Перевірити свій баланс.')
    async def balance(self, ctx: T84ApplicationContext):
        await ctx.user_instance.add_achievement(Achievement.get_from_key("ach_balance"), notify_user=True)

        await ctx.respond(
            f"Ваш баланс: **{ctx.user_instance.balance}** 💸 | **{ctx.user_instance.premium_balance}** 💎",
            ephemeral=True
        )

    @discord.slash_command(name='inventory', description='👤 Переглянути свій інвентар.')
    async def inventory(
            self, ctx: T84ApplicationContext, member: discord.Option(discord.Member, description="👤 Користувач") = None
    ):
        member = member or ctx.user

        user_instance, _ = await User.get_or_create(discord_id=member.id)

        embed = DefaultEmbed()
        embed.title = f"Інвентар користувача {member.display_name}"

        desc = ""
        for item in user_instance.inventory:
            desc += f"**{item}**\n"

        desc += \
            "\n💡 *Якщо ви шукаєте де можна перемкнути відображення ролей - пропишіть команду `/roles`*" \
                if member.id == ctx.user.id and desc else ""

        embed.description = \
            desc if desc else "*Пусто* 😢"

        await ctx.respond(embed=embed)

    @cooldown(1, 30.0, BucketType.user)
    @discord.slash_command(name='roles', description='👤 Перемикання своїх ролей.')
    async def user_roles(self, ctx: T84ApplicationContext):
        await ctx.defer(ephemeral=True)
        roles = set()

        for role in ctx.user.roles:
            if not role.id in self.bot.config.CHANGEABLE_ROLES:
                continue

            roles.add(role)

        stored_roles = await ctx.user_instance.get_stored_roles()

        enabled_roles = roles
        disabled_roles = set(stored_roles) - enabled_roles

        newly_added_roles = setdiff1d(list(roles), stored_roles)
        to_store = stored_roles.copy()
        to_store.extend(list(newly_added_roles))

        await ctx.user_instance.set_stored_roles(to_store)

        if len(enabled_roles) + len(disabled_roles) == 0:
            return await ctx.respond(content='❌ У вас немає ролей які можна було-б переключити.', ephemeral=True)

        embed = DefaultEmbed()
        embed.title = f'🎭 Ролі користувача {ctx.user.display_name}'
        embed.set_thumbnail(url=ctx.user.display_avatar)

        disabled = ' '.join(map(lambda x: x.mention, disabled_roles))
        enabled = ' '.join(map(lambda x: x.mention, enabled_roles))
        embed.description = f"**Ролі користувача {ctx.user.mention}:**\n\n" \
                            f"**🌑 Вимкнені:**\n{disabled}\n\n" \
                            f"**🌞 Ввімкнені:**\n{enabled}\n\n"

        view = discord.ui.View(disable_on_timeout=True)

        for _itm in enabled_roles:
            view.add_item(ToggleRole(_itm, True))

        for _itm in disabled_roles:
            view.add_item(ToggleRole(_itm, False))

        await ctx.respond(embed=embed, view=view)

def setup(bot: T84):
    bot.add_cog(Profile(bot))
