import json
import os
import logging
# import sentry_sdk
import asyncio
from dotenv import load_dotenv
from discord import ExtensionNotFound
from datetime import datetime as dt
from tortoise import connections
from pycord.multicog import apply_multicog

load_dotenv()

fmt = '[%(levelname)s] %(asctime)s - %(message)s'
file = f'logs/{dt.strftime(dt.now(), "[%b] %Y.%m.%d (%Hh%Mm%Ss)")}.log'
logging.basicConfig(level=logging.DEBUG, format=fmt, filename=file)

# sentry_debug = True if os.getenv("SENTRY_DEBUG") == "True" else False
# sentry_address = f"http://{os.getenv('SENTRY_PK')}@38.242.131.170:9000/2"

# sentry_sdk.init(
#    dsn=sentry_address,
#    debug=sentry_debug,
#    traces_sample_rate=1.0,
# )

import config
from src import bot_instance, GuildNotWhitelisted, T84ApplicationContext
from src.models import User
from src.database import db_init
from src.base_types import Unique


@bot_instance.check
async def overall_check(ctx: T84ApplicationContext):
    if ctx.guild_id not in (config.PARENT_GUILD, config.BACKEND_GUILD):
        await ctx.respond(
            content=f"❌ **Виконання цієї команди заборонено на зовнішніх серверах.**\n"
                    f"*Якщо ви переконані що це помилка - зв'яжіться з розробником `gigalegit-#0880`*\n\n"
                    f"Сервер бота -> {config.PG_INVITE}"
        )
        raise GuildNotWhitelisted(ctx.guild_id)

    if not ctx.bot.is_ready():
        await ctx.bot.wait_until_ready()

    # User creation if not present
    user, _ = await User.get_or_create(discord_id=ctx.user.id)

    ctx._user_instance = user

    return True


async def main():
    for cog in config.cogs:
        try:
            bot_instance.load_extension(f'src.cogs.{cog}')
            print(f'✅ Extension {cog} successfully loaded!')
        except ExtensionNotFound:
            print(f'❌ Failed to load extension {cog}')

    apply_multicog(bot_instance)

    unique_instances = json.dumps(Unique.__instances__, indent=4, default=str, ensure_ascii=False)
    logging.info(f"Unique instances processed: {unique_instances}")

    if bot_instance.debug:
        print(f'✔ Processed Unique instances: {unique_instances}')

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
        event_loop.run_until_complete(bot_instance.close())
        event_loop.run_until_complete(connections.close_all(discard=True))
        event_loop.stop()
