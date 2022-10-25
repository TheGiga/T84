import os
import config
from dotenv import load_dotenv

load_dotenv()

import sentry_sdk

sentry_sdk.init(
    dsn=f"http://{os.getenv('SENTRY_PK')}@38.242.131.170:9000/2",
    debug=bool(os.getenv("SENTRY_DEBUG")),
    traces_sample_rate=1.0,
)

from tortoise import run_async
from discord import ExtensionNotFound
from src import bot_instance

from src.database import db_init

if __name__ == "__main__":
    for cog in config.cogs:
        try:
            bot_instance.load_extension(cog)
            print(f'✅ Extension {cog} successfully loaded!')
        except ExtensionNotFound:
            print(f'❌ Failed to load extension {cog}')

    run_async(db_init())
    bot_instance.run(os.getenv("TOKEN"))
