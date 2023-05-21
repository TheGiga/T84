import discord
from discord import SlashCommandGroup, ButtonStyle

import config
from src import T84ApplicationContext, DefaultEmbed, NotEnoughPremiumCurrency, CouldNotSendDM, boolean_emoji, \
    BattlePassLevels
from src.bot import T84
from src.models import User
from discord.ext.tasks import loop


class BattlePassCog(discord.Cog):
    def __init__(self, bot):
        self.bot: T84 = bot
        self.cache = []
        self.caching_loop.start()

    battlepass_commands = SlashCommandGroup(name='battlepass', description="🔰 Команди баттл-пассу")

    @battlepass_commands.command(name='profile', description='🔰 Ваш прогресс у баттл-пассі цього сезону.')
    async def battlepass_progress(
            self, ctx: T84ApplicationContext, #season: discord.Option(int, description="Сезон") = config.CURRENT_BP_SEASON
    ):
        await ctx.defer()

        embed = await ctx.user_instance.get_battlepass_embed()

        await ctx.respond(embed=embed)

    # make it much user friendlier plspls me
    @battlepass_commands.command(name='rewards', description='🔰 Список нагород баттл-пассу поточного сезону.')
    async def battlepass_rewards(self, ctx: T84ApplicationContext, level: int):
        rewards = BattlePassLevels.get_by_level(level)

        embed = DefaultEmbed()
        embed.title = f"Нагороди {level}-ого рівню | Battle Pass"
        embed.description = str(rewards if rewards else "*Немає :(*")

        await ctx.respond(embed=embed)

    @battlepass_commands.command(
        name='booster', description='🔰 Якщо ви бустер серверу - ви можете отримати баттл-пасс безкоштовно!'
    )
    async def battlepass_booster(self, ctx: T84ApplicationContext):
        booster_role = ctx.guild.get_role(self.bot.config.BOOSTER_ROLE)

        if not booster_role in ctx.user.roles:
            return await ctx.respond(
                "** ❌ Ви не є бустером серверу!**\n"
                f"- Щоб отримати преміум баттл-пасс вам треба стати бустером серверу!\n\n"
                f"*Або придбати його за {config.BP_PREMIUM_COST} 💎, більше інформації -> "
                f"<#{config.DONATE_INFO_CHANNEL}>*",
                ephemeral=True
            )

        bp = await ctx.user_instance.get_battlepass_data()

        if bp.premium:
            return await ctx.respond(
                f"✅ Ви вже маєте **Преміум баттл-пасс `#{config.CURRENT_BP_SEASON}`**.", ephemeral=True
            )

        bp.premium = True
        await bp.save()

        await ctx.respond(
            f"✅ Ви успішно отримали **Преміум баттл-пасс `#{config.CURRENT_BP_SEASON}`**!"
        )
        await BattlePassLevels.PAID_INSTANT.apply_all(user=ctx.user_instance)

    @battlepass_commands.command(
        name='buy', description=f"🔰 Купити преміум баттл-пасс цього сезону. [Ціна: {config.BP_PREMIUM_COST} 💎]"
    )
    async def battlepass_buy(self, ctx: T84ApplicationContext):
        if config.BP_PREMIUM_COST > ctx.user_instance.premium_balance:
            raise NotEnoughPremiumCurrency

        await ctx.defer(ephemeral=True)

        bp = await ctx.user_instance.get_battlepass_data()

        if bp.premium:
            return await ctx.respond(f"✅ Ви вже маєте **Преміум баттл-пасс #{config.CURRENT_BP_SEASON}**.")

        async def button_callback(interaction: discord.Interaction):
            if config.BP_PREMIUM_COST > ctx.user_instance.premium_balance:
                raise NotEnoughPremiumCurrency

            await ctx.user_instance.add_premium_balance(-config.BP_PREMIUM_COST)

            view.disable_all_items()

            await interaction.message.edit(view=view)

            bp.premium = True
            await bp.save()

            await interaction.response.send_message(content='✅ Успішно!')
            await BattlePassLevels.PAID_INSTANT.apply_all(user=ctx.user_instance)


        view = discord.ui.View(timeout=30.0, disable_on_timeout=True)
        button = discord.ui.Button(label="Так!", emoji="✔️", style=ButtonStyle.green)
        button.callback = button_callback

        view.add_item(button)

        embed = DefaultEmbed()
        embed.title = "ДТВУ | Баттл-пасс"
        embed.colour = discord.Colour.green()
        embed.description = f'Ви дійсно бажаєте придбати "**Преміум Баттл-Пасс #{config.CURRENT_BP_SEASON}**" ?\n\n' \
                            f'*Якщо ви передумали - просто ігноруйте це повідомлення...*'

        try:
            await ctx.user_instance.send(embed=embed, view=view)
        except CouldNotSendDM:
            return await ctx.respond(
                "❌ **Бот не зміг написати вам до __ЛС__!**\n\n"
                f"Для подальших дій треба відкрити приватні повідомлення з ботом {ctx.me.mention} "
                f"та написати йому любе повідомлення. Після цього напишіть команду ще раз."
            )

        await ctx.respond("☑️ Для подальших дій перейдіть в __ЛС__ до бота.", ephemeral=True)

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot or message.guild.id != self.bot.config.PARENT_GUILD:
            return

        if message.author.id in self.cache:
            return

        user, _ = await User.get_or_create(discord_id=message.author.id)
        bp = await user.get_battlepass_data()

        await bp.add_xp(config.BP_XP_PER_MESSAGE)
        affected, rewards = await bp.update_level()

        if affected:
            embed = DefaultEmbed()
            embed.title = "Ви досягли нового рівню Баттл-Пассу!"

            if bp.premium:
                embed.colour = discord.Colour.blurple()

            embed.description = f'Нагороди:\n {rewards if rewards else "*На цьому рівні є тільки преміальні нагороди*"}'

            embed.add_field(name="🔘 Досвід BP", value=f'`{bp.xp}`')
            embed.add_field(name="♾️ Рівень BP", value=f'`{bp.level}`')
            embed.add_field(name="💎 Преміум", value=boolean_emoji(bp.premium))

            embed.set_thumbnail(url='https://i.imgur.com/BapZMjf.png')

            await message.reply(embed=embed)

        self.cache.append(user.discord_id)

    @loop(minutes=4)
    async def caching_loop(self):
        self.cache.clear()

def setup(bot):
    bot.add_cog(BattlePassCog(bot))
