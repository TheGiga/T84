import logging
from abc import ABC

import discord
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

    def help_command_embed(self) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.embed_background(), timestamp=discord.utils.utcnow())
        embed.title = 'Допомога'
        embed.set_footer(text='by gigalegit-#0880')

        slash_commands, slash_commands_count = '', 0

        for command in self.commands:
            match command.__class__:
                case discord.SlashCommandGroup:
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

    async def on_application_command_error(
            self, ctx: discord.ApplicationContext, error: discord.ApplicationCommandError
    ):
        if isinstance(error, GuildNotWhitelisted):
            return

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
            await ctx.send(
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
            )

        try:
            await ctx.respond(
                embed=discord.Embed(
                    title=error.__class__.__name__,
                    description=str(error),
                    color=discord.Colour.embed_background(),
                )
            )
        except discord.NotFound:
            pass

        # capture_exception(error)
        logging.error(error)
        raise error


bot_instance = T84(intents=_intents)


@bot_instance.event
async def on_ready():
    tprint("T84")
    print(f"Bot is ready, logged in as {bot_instance.user}")


@bot_instance.check
async def overall_check(ctx: discord.ApplicationContext):
    from src.models import Guild, User

    if ctx.guild_id not in (config.PARENT_GUILD, config.TESTING_GUILD):
        await ctx.respond(
            content=f"❌ **Виконання цієї команди заборонено на зовнішніх серверах.**\n"
                    f"*Якщо ви переконані що це помилка - зв'яжіться з розробником `gigalegit-#0880`*\n\n"
                    f"Сервер бота -> {config.PG_INVITE}"
        )
        raise GuildNotWhitelisted(ctx.guild_id)

    # Guild creation if not present | For future
    await Guild.get_or_create(discord_id=ctx.guild_id)

    # User creation if not present
    await User.get_or_create(discord_id=ctx.user.id)

    return True
