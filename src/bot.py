import logging
import os
import aiohttp
import discord
from logging import WARNING, ERROR, CRITICAL
from abc import ABC
from art import tprint
from discord import Webhook, Interaction
from discord.ext.commands import MissingPermissions
from discord.ext.commands import CommandOnCooldown
from discord.ext import tasks
from discord.errors import CheckFailure

import config
from .errors import GuildNotWhitelisted

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User

# from sentry_sdk import capture_exception

_intents = discord.Intents.default()
_intents.__setattr__("presences", True)
_intents.__setattr__("message_content", True)
_intents.__setattr__("members", True)


class T84ApplicationContext(discord.ApplicationContext):
    def __init__(self, bot: 'T84', interaction: Interaction):
        super().__init__(bot, interaction)
        self._user_instance = None

    @property
    def user_instance(self) -> 'User':
        """
        :return: User instance set during overall_check (main.py), instance of src.models.User
        """
        return self._user_instance


class T84(discord.Bot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

        self.config = config
        self.debug = False

        self.activity_updater.start()

        if os.getenv("BOT_DEBUG") == "True":
            self.debug = True
            logging.info("T84 Debug mode, aka testing.")

            self.config.PARENT_GUILD = self.config.BACKEND_GUILD
            self.config.PARENT_GUILD_MAIN_CHAT = self.config.BACKEND_CHAT
            self.config.EVENT_CHANNEL_ID = self.config.BACKEND_CHAT
            self.config.SELF_ROLES_IDS = [
                1049431166442279074, 1084615910242914426, 1084615904014368868,
                1084615903066476595, 1084615902185660476, 1084615896162635813
            ]
            self.config.SELF_ROLES_CHANNEL_ID = self.config.BACKEND_CHAT

    @property
    async def parent_guild(self) -> discord.Guild | None:
        return await discord.utils.get_or_fetch(self, 'guild', self.config.PARENT_GUILD)

    async def get_application_context(
            self, interaction: discord.Interaction, cls=T84ApplicationContext
    ):
        # The same method for custom application context.
        return await super().get_application_context(interaction, cls=cls)

    def help_command(self) -> list[discord.Embed]:
        embed = discord.Embed()
        embed.colour = discord.Colour.embed_background()
        embed.title = "Команди бота T84"
        embed.set_image(url="https://i.imgur.com/WozcNGD.png")

        raw_commands = self.commands.copy()

        ordinary_commands = ''

        slash_count = 0
        for slash_count, slash in enumerate(
                [
                    command
                    for command in raw_commands
                    if type(command) is discord.SlashCommand
                ], 1
        ):
            ordinary_commands += f'{slash.mention} » {slash.description}\n'
            raw_commands.remove(slash)

        embed.description = f'**Базові слеш-команди:** ({slash_count})\n{ordinary_commands}'

        group_embeds = []

        for group in [
            group
            for group in raw_commands
            if type(group) is discord.SlashCommandGroup and group.name != 'admin'
        ]:
            group_embed = discord.Embed()
            group_embed.colour = discord.Colour.embed_background()
            group_embed.title = f'/{group.name}'
            group_embed.set_image(url="https://i.imgur.com/WozcNGD.png")

            group_commands = list(group.walk_commands())
            description = ''

            for subgroup in [
                sg
                for sg in group_commands
                if type(sg) is discord.SlashCommandGroup
            ]:
                value = ''

                for subgroup_command in subgroup.walk_commands():
                    value += f' - {subgroup_command.mention} » {subgroup_command.description}\n'
                    group_commands.remove(subgroup_command)

                group_embed.add_field(name=f"**/{subgroup.qualified_name}**:\n", value=value, inline=False)
                group_commands.remove(subgroup)

            # At this point, all non discord.SlashCommand entries should be removed
            for group_command in group_commands:
                description += f"{group_command.mention} » {group_command.description}\n"

            group_embed.description = description

            group_embeds.append(group_embed)
            raw_commands.remove(group)

        return [embed, *group_embeds]

    async def on_ready(self):
        tprint("T84")
        print(f"✔ Bot is ready, logged in as {self.user}")

    @staticmethod
    async def send_critical_log(message: str, level: WARNING | ERROR | CRITICAL) -> None:
        """
        Message will be forwarded to local logging module + filesystem
        and also sent out via discord webhook if needed.

        :param level: level of log
        :param message: The message to be logged
        :return: None
        """

        logging.log(
            level=level,
            msg=message
        )

        content = f'`[{logging.getLevelName(level)}]` {message}'

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(os.getenv("LOGGING_WEBHOOK"), session=session)
            await webhook.send(content=content)

    async def on_application_command_error(
            self, ctx: discord.ApplicationContext, error: discord.ApplicationCommandError
    ):
        if isinstance(error, GuildNotWhitelisted):
            return

        elif isinstance(error, MissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red(), title='⚠ Заборонено!')
            embed.description = f"❌ Вам не дозволено виконання цієї команди!"
            await ctx.respond(embed=embed, ephemeral=True)
            return

        elif isinstance(error, CheckFailure):
            embed = discord.Embed(colour=discord.Colour.red(), title='⚠ Заборонено!')
            embed.description = f"❌ Помилка перевірки!"
            await ctx.respond(embed=embed, ephemeral=True)
            return

        elif isinstance(error, discord.NotFound):
            return

        elif isinstance(error, CommandOnCooldown):
            return await ctx.respond(
                content=f'❌ На цю команду діє кулдаун: `{round(error.cooldown.get_retry_after())} секунд`',
                ephemeral=True
            )

        elif isinstance(error, discord.ApplicationCommandInvokeError):
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

        else:
            await ctx.send(
                embed=discord.Embed(
                    title=error.__class__.__name__,
                    description=str(error),
                    color=discord.Colour.embed_background(),
                )
            )

        # capture_exception(error)
        await self.send_critical_log(str(error), logging.ERROR)
        raise error

    @tasks.loop(hours=1)
    async def activity_updater(self):
        await self.wait_until_ready()
        await self.change_presence(
            activity=discord.Streaming(
                name=f'/help | {len(self.commands)} Команд', url='https://twitch.tv/gigabit_0880'
            )
        )


bot_instance = T84(intents=_intents)
