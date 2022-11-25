import discord
import os
import logging
# import sentry_sdk
import asyncio
from dotenv import load_dotenv
from discord import ExtensionNotFound
from datetime import datetime as dt
from tortoise import connections

load_dotenv()

fmt = '[%(levelname)s] %(asctime)s - %(message)s'
file = f'logs/{dt.strftime(dt.now(), "[%b] %d.%m.%Y (%Hh%Mm%Ss)")}.log'
logging.basicConfig(level=logging.DEBUG, format=fmt, filename=file)

# sentry_debug = True if os.getenv("SENTRY_DEBUG") == "True" else False
# sentry_address = f"http://{os.getenv('SENTRY_PK')}@38.242.131.170:9000/2"

# sentry_sdk.init(
#    dsn=sentry_address,
#    debug=sentry_debug,
#    traces_sample_rate=1.0,
# )

import config
from src import bot_instance, GuildNotWhitelisted
from src.database import db_init


@bot_instance.check
async def overall_check(ctx: discord.ApplicationContext):
    from src.models import User

    if ctx.guild_id not in (config.PARENT_GUILD, config.BACKEND_GUILD):
        await ctx.respond(
            content=f"❌ **Виконання цієї команди заборонено на зовнішніх серверах.**\n"
                    f"*Якщо ви переконані що це помилка - зв'яжіться з розробником `gigalegit-#0880`*\n\n"
                    f"Сервер бота -> {config.PG_INVITE}"
        )
        raise GuildNotWhitelisted(ctx.guild_id)

    # User creation if not present
    await User.get_or_create(discord_id=ctx.user.id)

    checks = tuple(x.__name__ for x in ctx.command.checks)
    if "admin_check" in checks:
        await bot_instance.log(
            f"ADMIN COMMAND </{ctx.command.qualified_name}:{ctx.command.qualified_id}> "
            f"just used by {ctx.author} {ctx.author.mention}",
            logging.WARNING
        )

    return True


async def main():
    for cog in config.cogs:
        try:
            bot_instance.load_extension(cog)
            print(f'✅ Extension {cog} successfully loaded!')
        except ExtensionNotFound:
            print(f'❌ Failed to load extension {cog}')

    await db_init()
    await bot_instance.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop_policy().get_event_loop()

    try:
        event_loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        print("🛑 Shutting Down")
        if not bot_instance.is_closed():
            event_loop.run_until_complete(bot_instance.close())
        event_loop.run_until_complete(connections.close_all(discard=True))
        event_loop.stop()
