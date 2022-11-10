from math import sqrt, floor

import discord
from discord import NotFound
from tortoise import fields
from tortoise.models import Model

import config
from src import bot_instance, DefaultEmbed


class User(Model):
    id = fields.IntField(pk=True)
    discord_id = fields.IntField()
    xp = fields.IntField(default=0)
    level = fields.IntField(default=0)
    message_count = fields.IntField(default=0)
    balance = fields.IntField(default=0)
    achievements = fields.JSONField(default=[])

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

    @staticmethod
    def next_level_progress_bar(percent: int) -> str:
        raw_percents = percent // 10
        bar = ""

        for _ in range(raw_percents):
            bar += "🟨"

        final = bar.ljust(10, "⬛")
        return final

    @property
    def xp_tnl(self) -> int:
        """
        :return: INT: Amount of XP needed to reach next level.
        """
        xp_nl = self.level_to_xp(self.level + 1)
        xp_tnl = xp_nl - self.xp

        return xp_tnl

    async def add_xp(self, amount: int, notify_user: bool = False) -> None:
        self.xp += amount
        await self.save()

        if notify_user:
            discord_instance = await self.get_discord_instance()

            if not discord_instance.can_send(discord.Message, discord.Embed):
                return

            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ', url=config.PG_INVITE)
            embed.description = f"Вам нараховано **XP** у розмірі `{amount}`"

            await discord_instance.send(embed=embed)

    async def get_profile_embed(self) -> discord.Embed:
        member = await self.get_discord_instance()

        embed = DefaultEmbed()
        embed.title = f"**Профіль користувача {member.display_name}**"

        embed.add_field(name='⚖ Рівень', value=f'`{self.level}`')
        embed.add_field(name='🎈 Досвід', value=f'`{self.xp}`')
        embed.add_field(name='🔢 UID', value=f'`#{self.id}`')
        embed.set_thumbnail(url=member.display_avatar.url)

        xp_to_new_level = self.xp - self.level_to_xp(self.level)
        xp_new_level = self.level_to_xp(self.level + 1) - self.level_to_xp(self.level)

        percent = round((xp_to_new_level / xp_new_level) * 100)

        embed.description = f"""
                Прогрес до наступного рівню: `{self.xp}/{self.level_to_xp(self.level + 1)}`
                > ```{self.level} {self.next_level_progress_bar(percent)} {self.level + 1}```
                """

        # Placeholder image to make embed have the same width everytime
        embed.set_image(url="https://i.imgur.com/WozcNGD.png")

        return embed

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
                award = config.awards.get(i + 1)
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
