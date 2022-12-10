import discord

from src import T84ApplicationContext, DefaultEmbed
from src.achievements import Achievement
from src.bot import T84
from src.models import User
from src.shop import ShopItems, ShopItem

shop_roles = [
    item.value
    for item in ShopItems
    if item.value.value.code == "roles"
]

shop_roles_uids = [
    item.uid for item in shop_roles
]


class ToggleShopRoles(discord.ui.Select):
    def __init__(self, user_shop_roles: list[ShopItem]):
        options = [
            discord.SelectOption(label=item.label, emoji=item.emoji, value=str(item.uid))
            for item in user_shop_roles
        ]

        super().__init__(
            placeholder="Перемкнути відображення куплених ролей.",
            min_values=1,
            max_values=len(user_shop_roles),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        toggled_roles = ''

        for value in self.values:
            shop_item: ShopItem = ShopItem.get_from_id(int(value))
            role = await discord.utils.get_or_fetch(interaction.guild, 'role', shop_item.value.payload)

            if role in interaction.user.roles:
                await interaction.user.add_roles(role)
                toggled_roles += f'**+** {role.mention}\n\n'
            else:
                await interaction.user.remove_roles(role)
                toggled_roles += f'**-** {role.mention}\n\n'

        await interaction.response.send_message(content=toggled_roles, ephemeral=True)


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
        await ctx.user_instance.add_achievement(Achievement.get_from_id(2013), notify_user=True)

        await ctx.respond(f"Ваш баланс: **{ctx.user_instance.balance}** 💸", ephemeral=True)

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
            desc += f"**{item}**\n*`- {item.description if item.description else '(Без опису)'}`*\n\n"

        embed.description = desc if desc else "*Пусто* 😢"

        view = discord.ui.View()

        if ctx.author.id == member.id:

            user_shop_roles: list[ShopItem] = [  # type: ignore
                item
                for item in user_instance.inventory
                if item.uid in shop_roles_uids
            ]

            if len(user_shop_roles) > 0:
                view.add_item(ToggleShopRoles(user_shop_roles))

        await ctx.respond(embed=embed, view=view)


def setup(bot: T84):
    bot.add_cog(Profile(bot))
