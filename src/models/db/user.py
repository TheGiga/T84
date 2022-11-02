from math import sqrt, floor

import discord
from discord import NotFound
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

    @staticmethod
    def level_to_xp(level: int) -> int:
        xp = level // config.XP_MULTIPLIER
        xp = xp ** 2

        return floor(xp)

    @staticmethod
    def xp_to_level(xp: int) -> int:
        lvl_raw = config.XP_MULTIPLIER * sqrt(xp)

        return floor(lvl_raw)

    @property
    def xp_tnl(self) -> int:
        """
        :return: INT: Amount of XP needed to reach next level.
        """
        xp_nl = self.level_to_xp(self.level + 1)
        xp_tnl = xp_nl - self.xp

        return xp_tnl

    async def apply_reward(self, award: config.Reward, guild: discord.Guild) -> str:
        match award.reward_type:
            case "role":
                member_instance = await self.get_discord_instance(guild=guild)
                role = guild.get_role(award.value)

                if role is not None:
                    await member_instance.add_roles(role)
                    print(f"Rewarded {member_instance.name} with '{role.name}'")

                return f"<@&{award.value}>"
            case _:
                return "None"

    async def get_discord_instance(self, guild: discord.Guild = None) -> discord.User | discord.Member | None:
        try:
            if guild is None:
                user = await bot_instance.get_or_fetch_user(self.discord_id)

                return user
            else:
                # user = await guild.get_or_fetch_member(self.discord_id)
                user = await discord.utils.get_or_fetch(guild, 'member', self.discord_id, )

                return user
        except NotFound:
            return None

    async def update_levels(self, guild: discord.Guild) -> (int, bool, str | None):
        """
        Update user levels based on XP.

        level - current level of user

        affected - if level was changed - this parameter will be True

        reward - the thing user achieved with new level
        
        :return: (level: int, affected: bool, rewards: str | None)
        """

        level = self.xp_to_level(self.xp)
        level_gain = level - self.level

        affected = True
        rewards = ""

        if level_gain > 0:
            member_instance = await self.get_discord_instance(guild=guild)

            if member_instance is None:
                return level, False, rewards

            for i in range(self.level, level):
                award = config.awards.get(i+1)
                if award is None:
                    continue

                apl_value = await self.apply_reward(award=award, guild=guild)

                rewards += f'{apl_value} '
        else:
            affected = False

        self.level = level
        await self.save()

        rewards = rewards if len(rewards) > 0 else None
        return level, affected, rewards
