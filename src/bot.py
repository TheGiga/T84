import discord
from art import tprint


_intents = discord.Intents.default()
_intents.__setattr__("messages", True)
_intents.__setattr__("message_content", True)

bot_instance = discord.Bot(intents=_intents)


@bot_instance.event
async def on_ready():
    tprint("T84")
    print(f"Bot is ready, logged in as {bot_instance.user}")

