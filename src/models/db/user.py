from math import sqrt, floor

import discord
from tortoise import fields
from tortoise.models import Model

import config
from src import bot_instance


class User(Model):
    id = fields.IntField(pk=True)
    discord_id = fields.IntField()
    xp = fields.IntField(default=0)
    level = fields.IntField(default=0)

    def __int__(self):
        return self.discord_id

    def __str__(self):
        return f"[ User with id {self.discord_id} ]"

    def __repr__(self):
        return f'User({self.discord_id=}, {self.id=})'

    async def get_discord_instance(self, guild: discord.Guild = None) -> discord.User | discord.Member | None:
        if guild is None:
            user = await bot_instance.get_or_fetch_user(self.discord_id)

            return user
        else:
            # user = await guild.get_or_fetch_member(self.discord_id)
            user = await discord.utils.get_or_fetch(guild, 'member', self.discord_id, )

            return user

    async def update_levels(self) -> (int, bool):
        """
        Update user levels based on XP.
        level - current level of user
        affected - if level was changed - this parameter will be True
        
        :return: (level: int, affected: bool)
        """

        level_raw = 0.3 * sqrt(self.xp)
        level = floor(level_raw)

        affected = False

        if self.level != level:
            self.level = level
            await self.save()

            for key in config.awards:
                if key <= level:
                    role = config.awards[key]

                    guild = bot_instance.get_guild(config.PARENT_GUILD)
                    role = guild.get_role(role)
                    member = await self.get_discord_instance(guild=guild)
                    if role not in member.roles:
                        await member.add_roles(role)

            affected = True

        return level, affected


