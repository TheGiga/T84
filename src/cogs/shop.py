import discord

from src import DefaultEmbed
from src.base_types import Unique
from src.bot import T84
from src.models import User
from src.shop import ShopItems, ShopItem
from src.static import assets


class ConfirmationButton(discord.ui.Button):
    def __init__(self, cart: list, total_cost: int, buyer: User):
        super().__init__()

        self.user = buyer
        self.cost = total_cost
        self.cart: list[ShopItem] = cart

        self.style = discord.ButtonStyle.green
        self.label = "Підтверджую"
        self.emoji = "✅"

    async def callback(self, interaction: discord.Interaction):
        self.view.disable_all_items()
        await interaction.message.edit(view=self.view)

        if self.user.balance < self.cost:
            return await interaction.response.send_message("❌ У вас недостатньо балансу для придбання.", ephemeral=True)

        await self.user.add_balance(-self.cost)

        for cart_item in self.cart:
            await cart_item.give(self.user)

        await interaction.response.send_message(
            f"✅ Операція прошла успішно!\n\nВаш баланс: {self.user.balance} 💸", ephemeral=True
        )


class Select(discord.ui.Select):
    def __init__(self, shop_items: tuple):
        options = [
            discord.SelectOption(
                emoji=x.value.emoji, label=x.value.label, value=str(x.value.uid)
            ) for x in shop_items
        ]

        super().__init__(
            placeholder="Виберіть елементи для придбання...",
            options=options,
            max_values=len(options)
        )

    async def callback(self, interaction: discord.Interaction):
        user, _ = await User.get_or_create(discord_id=interaction.user.id)

        cart = []
        cart_cost = 0  # sum(tuple(x.cost for x in cart))
        cart_items_formatted = ""

        for item in self.values:
            shop_item: ShopItem = Unique.get_from_id(int(item))
            cart.append(shop_item)
            cart_cost += shop_item.cost
            cart_items_formatted += f'• **{shop_item.label}** - {shop_item.cost} 💸\n'

        embed = DefaultEmbed()

        embed.description = f"""
                {cart_items_formatted}
                Сума: **{cart_cost} 💸**
            """

        if cart_cost > user.balance:
            embed.colour = discord.Colour.red()
            embed.title = "❌ Вам не вистачає балансу для придбання"

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.send_message(content='✅ Для подальших дій перейдіть в ЛС до боту.', ephemeral=True)

        embed.title = "✅ Підтвердіть своє придбання"
        embed.colour = discord.Colour.green()

        view = discord.ui.View()
        view.add_item(ConfirmationButton(cart, cart_cost, user))

        await interaction.user.send(
            content="⚠ Якщо ви передумали, то просто ігноруйте це повідомлення.",
            embed=embed, view=view
        )


class Shop(discord.Cog):
    def __init__(self, bot: T84):
        self.bot = bot

    @discord.slash_command(name='shop', description='🏬 Магазин серверу.')
    async def shop(
            self, ctx: discord.ApplicationContext, shop_type: discord.Option(name="category", choices=['roles'])
    ):
        await ctx.defer()

        shop_items = tuple(x for x in ShopItems if x.value.value.code == shop_type)

        embed = DefaultEmbed()
        embed.title = f"🛍️ Магазин серверу | {shop_type.upper()}"

        desc = ""

        for item in shop_items:
            desc += f"{f'<@&{item.value.value.payload}>' if shop_type == 'roles' else item.value.name}" \
                    f"\n*`- {item.value.description if item.value.description is not None else '(Без опису)'}`*" \
                    f"\n• {item.value.cost} 💸\n\n" \

        embed.description = desc
        embed.set_image(url=assets.SHOP_IMAGE)

        view = discord.ui.View()
        select = Select(shop_items)

        view.add_item(select)

        await ctx.respond(embed=embed, view=view)


def setup(bot: T84):
    bot.add_cog(Shop(bot=bot))
