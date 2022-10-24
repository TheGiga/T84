import discord
from discord.ext.commands import MissingPermissions

import config
from art import tprint
from .errors import GuildNotWhitelisted


_intents = discord.Intents.default()
_intents.__setattr__("messages", True)
_intents.__setattr__("message_content", True)

bot_instance = discord.Bot(intents=_intents)


@bot_instance.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, GuildNotWhitelisted):
        return

    if isinstance(error, MissingPermissions):
        embed = discord.Embed(colour=discord.Colour.red(), title='⚠ Заборонено!')
        embed.description = f"❌ Вам не дозволено виконання цієї команди!"
        await ctx.respond()
        return


# Global command check
@bot_instance.check
async def overall_check(ctx: discord.ApplicationContext):
    from src.models import Guild, User
    # Guild creation if not present

    await Guild.get_or_create(discord_id=ctx.guild_id)

    if ctx.guild_id not in [config.PARENT_GUILD, config.TESTING_GUILD]:
        await ctx.respond(
            content=f"❌ **Виконання цієї команди заборонено на зовнішніх серверах.**\n"
                    f"*Якщо ви переконані що це помилка - зв'яжіться з розробником `gigalegit-#0880`*\n\n"
                    f"Сервер бота -> {config.PG_INVITE}"
        )
        raise GuildNotWhitelisted(ctx.guild_id)

    # User creation if not present
    await User.get_or_create(discord_id=ctx.user.id)

    return True


@bot_instance.event
async def on_ready():
    tprint("T84")
    print(f"Bot is ready, logged in as {bot_instance.user}")
