import discord
from art import tprint

_intents = discord.Intents.default()
_intents.__setattr__("messages", True)
_intents.__setattr__("message_content", True)

bot_instance = discord.Bot(intents=_intents)


@bot_instance.check
async def overall_check(ctx: discord.ApplicationContext):
    from src.models import Guild, User
    # Guild creation if not present
    await Guild.get_or_create(discord_id=ctx.guild.id)

    # User creation if not present
    await User.get_or_create(discord_id=ctx.user.id)

    return True


@bot_instance.event
async def on_ready():
    tprint("T84")
    print(f"Bot is ready, logged in as {bot_instance.user}")
