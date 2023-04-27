import discord
from discord import ButtonStyle
from discord.ext.commands import cooldown, BucketType
from numpy import setdiff1d

from src import T84ApplicationContext, DefaultEmbed
from src.achievements import Achievement
from src.bot import T84
from src.models import User

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
        member = member or ctx.author

        user_instance, _ = await User.get_or_create(discord_id=member.id)

        embed = DefaultEmbed()
        embed.title = f"Інвентар користувача {member.display_name}"

        desc = ""
        for item in user_instance.inventory:
            desc += f"**{item}**\n\n"

        embed.description = desc if desc else "*Пусто* 😢"

        await ctx.respond(embed=embed)

    @cooldown(1, 30.0, BucketType.user)
    @discord.slash_command(name='roles', description='👤 Перемикання своїх ролей.')
    async def change_roles(self, ctx: T84ApplicationContext):
        await ctx.defer(ephemeral=True)
        roles = set()

        for role in ctx.user.roles:
            if not role.id in self.bot.config.CHANGEABLE_ROLES:
                continue

            roles.add(role)

        stored_roles = await ctx.user_instance.get_stored_roles()
        newly_added_roles = setdiff1d(list(roles), stored_roles)
        to_store = stored_roles.copy()
        to_store.extend(list(newly_added_roles))

        await ctx.user_instance.set_stored_roles(to_store)

        for stored_role in stored_roles:
            if not stored_role.id in self.bot.config.CHANGEABLE_ROLES:
                continue

            roles.add(stored_role)

        if len(roles) == 0:
            return await ctx.respond(content='❌ У вас немає ролей які можна було-б переключити.', ephemeral=True)

        embed = DefaultEmbed()
        embed.title = f'🎭 Ролі користувача {ctx.user.display_name}'
        embed.set_thumbnail(url=ctx.user.display_avatar)

        desc = ' '.join(map(lambda x: x.mention, roles))
        embed.description = f"**Ролі користувача {ctx.user.mention}:\n**{desc}\n\nОберіть ролі нижче для налаштування"

        async def dropdown_callback(interaction: discord.Interaction):
            raw_roles_data = map(lambda x: int(x), interaction.data.get('values'))
            roles_to_change = [r for r in roles if r.id in raw_roles_data]

            async def button_callback(inner: discord.Interaction):
                custom_id = inner.data.get('custom_id')
                inner_role = ctx.guild.get_role(int(custom_id))

                item = inner_view.get_item(custom_id=custom_id)
                inner_view.remove_item(item)

                if not inner_role in ctx.user.roles:
                    await ctx.user.add_roles(inner_role)
                    item.style = ButtonStyle.green # type: ignore
                else:
                    await ctx.user.remove_roles(inner_role)
                    item.style = ButtonStyle.red  # type: ignore

                inner_view.add_item(item)

                await inner.response.edit_message(view=inner_view)


            inner_view = discord.ui.View(timeout=45.0, disable_on_timeout=True)

            for target_role in roles_to_change:
                button = discord.ui.Button(
                    label=target_role.name, emoji=target_role.unicode_emoji, custom_id=str(target_role.id)
                )
                button.callback = button_callback

                if target_role in ctx.user.roles:
                    button.style = ButtonStyle.green
                else:
                    button.style = ButtonStyle.red

                inner_view.add_item(button)

            await interaction.response.send_message(
                "Красним відображаються вимкнуті ролі, зеленим - увімкнуті.\n**Переключайте їх натискаючи на кнопки.**",
                view=inner_view, ephemeral=True
            )

        select = discord.ui.Select(max_values=10 if len(roles) > 10 else len(roles))
        select.callback = dropdown_callback

        select.options = [
            discord.SelectOption(label=x.name, emoji=x.unicode_emoji, value=str(x.id)) for x in roles
        ]

        view = discord.ui.View(timeout=15.0, disable_on_timeout=True)
        view.add_item(select)

        await ctx.respond(embed=embed, view=view)


def setup(bot: T84):
    bot.add_cog(Profile(bot))
