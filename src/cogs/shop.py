import discord
from discord.ext.commands import BucketType, cooldown

from src import T84ApplicationContext, NotEnoughCurrency, NotEnoughPremiumCurrency
from src import shop
from src.models import User
from src.static.assets import SHOP_IMAGE

class BuyButton(discord.ui.Button):
    def __init__(self, target_item: shop.ShopItem, target_user: User):
        super().__init__()
        self.item = target_item
        self.user = target_user

    async def callback(self, interaction: discord.Interaction):
        try:
            if self.item.reward in self.user.inventory:
                return await interaction.response.send_message("✋ Ви вже маєте цей предмет!", ephemeral=True)

            await self.item.apply(user=self.user)

            await interaction.response.send_message(f"☑️ Ви успішно придбали {self.item.reward}", ephemeral=True)
        except (NotEnoughCurrency,NotEnoughPremiumCurrency):
            return await interaction.response.send_message("❌ У вас недостатньо коштів!", ephemeral=True)


class ServerShop(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1, 60, BucketType.user)
    @discord.slash_command(name="shop", description='💰 Магазин серверу')
    async def shop(self, ctx: T84ApplicationContext, category: discord.Option(str, choices=shop.SHOP_CATEGORIES)):
        await ctx.defer(ephemeral=True)
        shop_items = [item for item in shop.SHOP_ITEMS if item.category == category]

        embed = discord.Embed(title='💰 Магазин',colour=discord.Colour.green())
        embed.set_image(url=SHOP_IMAGE)
        description = ""
        view = discord.ui.View(timeout=45.0, disable_on_timeout=True)

        for item in shop_items:
            description += f'* {item.reward} - `{item.price} {"💎" if item.premium else "💸"}`\n'
            button = BuyButton(item, ctx.user_instance)
            button.emoji = item.emoji
            button.label = item.name

            view.add_item(button)

        embed.description = f"{description}\n**⚠️ При натисканні на кнопку - ви одразу купуєте обраний предмет!**"

        await ctx.user_instance.send(embed=embed, view=view)
        await ctx.respond(
            "☑️ **Бот відправив вам меню магазина!**\n\n"
            "*Якщо повідомлення не дійшло, можливо у вас закриті приватні повідомлення з ботом або сервером.*",
            ephemeral=True
        )





def setup(bot):
    bot.add_cog(ServerShop(bot))
