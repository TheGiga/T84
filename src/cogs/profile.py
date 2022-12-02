import discord

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
        member = member or ctx.author

        user, _ = await User.get_or_create(discord_id=member.id)

        embed = await user.get_profile_embed()

        await ctx.respond(embed=embed)

    @discord.slash_command(name='balance', description='👤 Перевірити свій баланс.')
    async def balance(self, ctx: T84ApplicationContext):
        await ctx.user_instance.add_achievement(Achievement.get_from_id(2013), notify_user=True)

        await ctx.respond(f"Ваш баланс: **{ctx.user_instance.balance}** 💸", ephemeral=True)

    @discord.slash_command(name='inventory', description='👤 Переглянути свій інвентар.')
    async def inventory(self, ctx: T84ApplicationContext):
        embed = DefaultEmbed()
        embed.title = f"Інвентар користувача {ctx.author.display_name}"

        desc = ""
        for item in ctx.user_instance.inventory:
            desc += f"**{item}**\n*`- {item.description}`*\n\n"

        embed.description = desc

        await ctx.respond(embed=embed)


def setup(bot: T84):
    bot.add_cog(Profile(bot))
