import os
from datetime import datetime as dt
from dotenv import load_dotenv

load_dotenv()

import config
import logging

# import sentry_sdk

# sentry_debug = True if os.getenv("SENTRY_DEBUG") == "True" else False
# sentry_address = f"http://{os.getenv('SENTRY_PK')}@38.242.131.170:9000/2"

# sentry_sdk.init(
#    dsn=sentry_address,
#    debug=sentry_debug,
#    traces_sample_rate=1.0,
# )

from tortoise import run_async
from discord import ExtensionNotFound
from src import bot_instance

from src.database import db_init


def main():
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    file = f'logs/{dt.strftime(dt.utcnow(), "[%b] %d.%m.%Y (%Hh%Mm%Ss)")}.log'
    logging.basicConfig(level=logging.DEBUG, format=fmt, filename=file)

    for cog in config.cogs:
        try:
            bot_instance.load_extension(cog)
            print(f'✅ Extension {cog} successfully loaded!')
        except ExtensionNotFound:
            print(f'❌ Failed to load extension {cog}')

    run_async(db_init())
    bot_instance.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
