import os
import config
from discord import ExtensionNotFound
from src import bot_instance
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    for cog in config.cogs:
        try:
            bot_instance.load_extension(cog)
            print(f'✅ Extension {cog} successfully loaded!')
        except ExtensionNotFound:
            print(f'❌ Failed to load extension {cog}')

    bot_instance.run(os.getenv("TOKEN"))
