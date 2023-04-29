import calendar
import datetime

import discord
from discord.ext.commands import has_permissions, cooldown, BucketType

from src import DefaultEmbed
from src.bot import T84, T84ApplicationContext
from src.models import User
from src.reasons import Reasons

async def reasons(ctx: discord.AutocompleteContext):
    return [x.value.name for x in Reasons if x.value.name.startswith(ctx.value)]


class Moderation(discord.Cog):
    def __init__(self, bot):
        self.bot: T84 = bot

    @has_permissions(moderate_members=True)
    @cooldown(5, 60, BucketType.user)
    @discord.slash_command(name='mute', description='👮 Команда модератора: МУТ')
    async def mute(
            self, ctx: T84ApplicationContext, member: discord.Option(discord.Member),
            reason: discord.Option(autocomplete=reasons, description='Причина покарання'),
            duration: discord.Option(int, description="Час в хвилинах")
    ):
        if ctx.user.top_role.position < member.top_role.position:
            return await ctx.respond(
                content="❌ Неможливо задати покарання для користувача з рол'ю вище вашої.", ephemeral=True
            )

        await ctx.defer(ephemeral=True)
        member_instance, _ = await User.get_or_create(discord_id=member.id)
        duration = datetime.timedelta(minutes=duration)
        duration_timestamp = calendar.timegm((datetime.datetime.utcnow() + duration).timetuple())

        await member_instance.timeout(reason, duration, moderator=ctx.user)
        await ctx.respond(
            f"☑️ Ви успішно видали тайм-аут користувачу {member.mention}\n"
            f"⏰ Строком до <t:{duration_timestamp}:f>\n"
            f"🔨 За причиною `{reason}`"
        )

        embed = DefaultEmbed()
        embed.title = f"⚠️ Користувача {member.display_name} було покарано!"
        embed.description = f'Користувачу {member.mention} було видано тайм-аут модератором {ctx.user.mention}\n\n' \
                            f'**Причина: `{reason}`**'

        await ctx.send(embed=embed)







def setup(bot):
    bot.add_cog(Moderation(bot))
