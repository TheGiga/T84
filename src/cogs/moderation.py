import logging

import discord
from discord.ext.commands import has_permissions, cooldown, BucketType

from src import DefaultEmbed
from src.bot import T84, T84ApplicationContext
from src.reasons import Reasons

reasons = [
    discord.OptionChoice(x.value.name, str(x.value.id))
    for x in Reasons
]


class Moderation(discord.Cog):
    def __init__(self, bot):
        self.bot: T84 = bot

    moderation = discord.SlashCommandGroup(name='moderation', description='👮 Команди модератора.')

    @has_permissions(moderate_members=True)
    @cooldown(3, 60, BucketType.user)
    @moderation.command(name='action', description='👮 Команда модератора: ПОКАРАННЯ')
    async def mute(self, ctx: T84ApplicationContext, member: discord.Option(discord.Member),
                   reason: discord.Option(
                       choices=reasons, description='Причина покарання.'
                   )):
        # "Reason id is 7, but indexing starts at 0, so I decrease it by 1"
        enum_reason = Reasons.get_from_id(int(reason))

        await ctx.defer(ephemeral=True)

        if ctx.user.top_role.position < member.top_role.position:
            return await ctx.respond(
                content="❌ Неможливо задати покарання для користувача з рол'ю вище вашої.", ephemeral=True
            )

        embed = DefaultEmbed()
        embed.description = f'**Причина:** `{enum_reason.name}`'
        embed.add_field(name='👮 Модератор', value=ctx.author.mention)
        embed.add_field(name='⏰ Термін', value=str(enum_reason.duration))

        match enum_reason.action:
            case 'timeout':
                embed.title = f'Вам було видано мут на сервері ДТВУ.'
                embed.colour = discord.Colour.orange()

                try:
                    await member.send(embed=embed)
                except discord.Forbidden:
                    pass

                await member.timeout_for(duration=enum_reason.duration, reason=enum_reason.name)

            case 'ban':
                embed.title = f'Вам було видано БАН на сервері ДТВУ!'
                # TODO: Сделать ебучий разбан по времени потом))
                #embed.add_field(2, name='⏰ Термін', value='__НАЗАВЖДИ__')  # value=str(enum_reason.duration))#
                embed.colour = discord.Colour.red()

                try:
                    await member.send(embed=embed)
                except discord.Forbidden:
                    pass

                await member.ban(reason=enum_reason.name)

        await self.bot.send_critical_log(
            message=f'Користувач {member.mention} `({member.id})` '
                    f'був покараний модератором {ctx.author.mention} `({ctx.author.id})` '
                    f'за причиною: `{enum_reason.name}`', level=logging.INFO
        )

        await ctx.respond(
            content=f'☑️ Користувач {member.mention} успішно покараний за причиною: `{enum_reason.name}`',
            ephemeral=True
        )

        await ctx.send(
            f'⚠️ **Користувача {member.mention} було покарано модератором {ctx.author.mention}.**\n'
            f'> Причина: `{enum_reason.name}` ||Термін: `{enum_reason.duration}`||'
        )


def setup(bot):
    bot.add_cog(Moderation(bot))
