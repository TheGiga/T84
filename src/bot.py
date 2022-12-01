import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
import os
from abc import ABC

import aiohttp
import discord
from discord import Webhook
from discord.ext.commands import MissingPermissions
from discord.errors import CheckFailure

import config
from art import tprint
from .errors import GuildNotWhitelisted

# from sentry_sdk import capture_exception

_intents = discord.Intents.default()
_intents.__setattr__("messages", True)
_intents.__setattr__("message_content", True)
_intents.__setattr__("members", True)


class T84(discord.Bot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

        self.config = config
        self.debug = False

        if os.getenv("BOT_DEBUG") == "True":
            self.debug = True
            logging.info("T84 Debug mode, aka testing.")

            self.config.PARENT_GUILD = self.config.BACKEND_GUILD
            self.config.PARENT_GUILD_MAIN_CHAT = self.config.BACKEND_CHAT
            self.config.EVENT_CHANNEL_ID = self.config.BACKEND_CHAT

    # TODO: Should be re-written vvv
    def help_command_embed(self) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.embed_background(), timestamp=discord.utils.utcnow())
        embed.title = 'Допомога'
        embed.set_footer(text='by gigalegit-#0880')

        slash_commands, slash_commands_count = '', 0

        for command in self.commands:
            match command.__class__:
                case discord.SlashCommandGroup:
                    if command.name == "admin":
                        continue

                    sub_commands = ''
                    for sub_command in command.subcommands:
                        sub_commands += f'> `{sub_command.name}` - {sub_command.description}\n'
                    embed.add_field(name=f'/{command.qualified_name}', value=sub_commands)
                case discord.SlashCommand:
                    slash_commands += f'{command.mention} - {command.description}\n'
                    slash_commands_count += 1
                case _:
                    continue

        embed.description = f"""
            **Слеш-команди**: `({slash_commands_count})`
            {slash_commands}
        """

        return embed

    async def on_ready(self):
        tprint("T84")
        print(f"✔ Bot is ready, logged in as {self.user}")

    @staticmethod
    async def log(message: str, level: DEBUG | INFO | WARNING | ERROR | CRITICAL) -> None:
        """
        Message will be forwarded to local logging module and filesystem
        and also sent out via discord webhook if needed.

        :param level: level of log
        :param message: The message to be logged
        :return: None
        """

        logging.log(
            level=level,
            msg=message
        )

        if level >= INFO:
            content = f'`[{logging.getLevelName(level)}]` {message}'

            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(os.getenv("LOGGING_WEBHOOK"), session=session)
                await webhook.send(content=content)

    async def on_application_command_error(
            self, ctx: discord.ApplicationContext, error: discord.ApplicationCommandError
    ):
        if isinstance(error, GuildNotWhitelisted):
            return

        await ctx.defer(ephemeral=True)

        if isinstance(error, MissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red(), title='⚠ Заборонено!')
            embed.description = f"❌ Вам не дозволено виконання цієї команди!"
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, CheckFailure):
            embed = discord.Embed(colour=discord.Colour.red(), title='⚠ Заборонено!')
            embed.description = f"❌ Помилка перевірки!"
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, discord.ApplicationCommandInvokeError):
            await ctx.respond(
                "Сталася невідома помилка, я доповів про цей кейс розробнику.\n\n"
                "Якщо це буде повторюватись - напишіть розробнику: `gigalegit-#0880`\n"
                "Якщо вам щось терміново потрібно - приєднуйтесь до серверу бота. *(кнопка нижче)*",
                view=discord.ui.View(
                    discord.ui.Button(
                        label="Сервер Бота", url=config.PG_INVITE
                    ),
                    discord.ui.Button(
                        label="GitHub Репозиторій",
                        url="https://github.com/TheGiga/T84",
                    ),
                ),
                ephemeral=False
            )

        await ctx.send(
            embed=discord.Embed(
                title=error.__class__.__name__,
                description=str(error),
                color=discord.Colour.embed_background(),
            )
        )

        # capture_exception(error)
        await self.log(str(error), logging.ERROR)
        raise error


bot_instance = T84(intents=_intents)
