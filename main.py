import os
import config
from dotenv import load_dotenv

load_dotenv()

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
