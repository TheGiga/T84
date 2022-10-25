import discord
from discord.ext.commands import MissingPermissions

import config
from art import tprint
from .errors import GuildNotWhitelisted

_intents = discord.Intents.default()
_intents.__setattr__("messages", True)
_intents.__setattr__("message_content", True)

bot_instance = discord.Bot(intents=_intents)


def help_command_embed() -> discord.Embed:
    embed = discord.Embed(colour=discord.Colour.embed_background(), timestamp=discord.utils.utcnow())
    embed.title = 'Допомога'
    embed.set_footer(text='by gigalegit-#0880')

    slash_commands, slash_commands_count = '', 0

    for command in bot_instance.commands:
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


@bot_instance.event
async def on_application_command_error(
        ctx: discord.ApplicationContext, error: discord.ApplicationCommandError
):
    if isinstance(error, GuildNotWhitelisted):
        return
    elif isinstance(error, MissingPermissions):
        embed = discord.Embed(colour=discord.Colour.red(), title='⚠ Заборонено!')
        embed.description = f"❌ Вам не дозволено виконання цієї команди!"
        await ctx.respond(embed=embed)
        return

    if isinstance(error, discord.ApplicationCommandInvokeError):
        await ctx.respond(
            "Сталася невідома помилка, якщо це повторюється - напишіть розробнику бота: `gigalegit-#0880` "
            "Також, приєднуйтесь до сервера бота.",
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

    await ctx.respond(
        embed=discord.Embed(
            title=error.__class__.__name__,
            description=str(error),
            color=discord.Colour.embed_background(),
        )
    )

    raise error


# Global command check
@bot_instance.check
async def overall_check(ctx: discord.ApplicationContext):
    from src.models import Guild, User
    # Guild creation if not present

    await Guild.get_or_create(discord_id=ctx.guild_id)

    if ctx.guild_id not in [config.PARENT_GUILD, config.TESTING_GUILD]:
        await ctx.respond(
            content=f"❌ **Виконання цієї команди заборонено на зовнішніх серверах.**\n"
                    f"*Якщо ви переконані що це помилка - зв'яжіться з розробником `gigalegit-#0880`*\n\n"
                    f"Сервер бота -> {config.PG_INVITE}"
        )
        raise GuildNotWhitelisted(ctx.guild_id)

    # User creation if not present
    await User.get_or_create(discord_id=ctx.user.id)

    return True


@bot_instance.event
async def on_ready():
    tprint("T84")
    print(f"Bot is ready, logged in as {bot_instance.user}")
