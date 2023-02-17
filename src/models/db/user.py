import logging
from math import sqrt, floor

import discord
from discord import NotFound
from tortoise import fields
from tortoise.models import Model

import config
from src import bot_instance, DefaultEmbed
from src.base_types import Unique, Inventoriable
from src.utils import progress_bar

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.achievements import Achievement, MsgCountAchievement


class User(Model):
    # Basic

    id = fields.IntField(pk=True)
    discord_id = fields.IntField()

    # Variables

    beta = fields.BooleanField(default=False)

    # Data

    xp = fields.IntField(default=0)
    level = fields.IntField(default=0)
    message_count = fields.IntField(default=0)
    balance = fields.IntField(default=0)
    premium_balance = fields.IntField(default=0)

    # Storage-able

    _achievements = fields.JSONField(source_field="achievements", default=[])
    _inventory = fields.JSONField(source_field="inventory", default=[])

    # Other
    xp_multiplier = fields.FloatField(default=1.0)

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
    def inventory(self) -> list[Unique | Inventoriable]:
        return [
            Unique.get_from_id(uid)
            for uid in self._inventory
        ]

    @property
    def achievements(self) -> list['Achievement']:
        return [
            Unique.get_from_id(uid)
            for uid in self._achievements
        ]

    @property
    def xp_tnl(self) -> int:
        """
        :return: INT: Amount of XP needed to reach next level.
        """
        xp_nl = self.level_to_xp(self.level + 1)
        xp_tnl = xp_nl - self.xp

        return xp_tnl

    @property
    def l_tnl_percent(self) -> int:
        """From current level to new level in percents"""
        xp_to_new_level = self.xp - self.level_to_xp(self.level)
        xp_new_level = self.level_to_xp(self.level + 1) - self.level_to_xp(self.level)

        return round((xp_to_new_level / xp_new_level) * 100)

    async def send_embed(self, embed: discord.Embed) -> None:
        discord_instance = await self.get_discord_instance()

        try:
            await discord_instance.send(embed=embed)
        except discord.Forbidden:
            logging.info(f"Couldn't send message to {discord_instance.id}, most likely due to closed DM's.")
            pass

    async def add_inventory_item(self, item: Unique) -> None:
        """
        Note: Item should be an instance of src.base_types.Inventoriable

        :param item: Unique (src.base_types.Unique) item
        :return: None
        """
        inventory = list(self._inventory)

        if item.uid in inventory:
            return

        if not issubclass(item.__class__, Inventoriable):
            return

        inventory.append(item.uid)
        self._inventory = inventory
        await self.save()

    async def add_balance(
            self, amount: int, notify_user: bool = False, additional_message: str = None
    ) -> None:
        self.balance += amount
        await self.save()

        if notify_user:
            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ', url=config.PG_INVITE)
            embed.description = f"Вам нараховано 💸 **Баланс** у розмірі `{amount}`" \
                                f"\n{additional_message if additional_message is not None else ''}"
            embed.colour = discord.Colour.gold()
            try:
                await self.send_embed(embed)
            except discord.HTTPException:
                pass

    async def add_premium_balance(self, amount: int, notify_user: bool = False) -> None:
        self.premium_balance += amount
        await self.save()

        if notify_user:
            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ', url=config.PG_INVITE)
            embed.description = f"Вам нараховано 💎 **Преміум баланс** у розмірі `{amount}`"
            embed.colour = discord.Colour.blue()

            try:
                await self.send_embed(embed)
            except discord.HTTPException:
                pass

    async def add_achievement(
            self, achievement: 'Achievement' or 'MsgCountAchievement', notify_user: bool = False
    ) -> None:
        current_achievements = list(self._achievements)
        if achievement.uid in current_achievements:
            return

        current_achievements.append(achievement.uid)
        self._achievements = current_achievements
        await self.save()

        if notify_user:
            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ | Досягнення', url=config.PG_INVITE)
            embed.title = f'🔹 {achievement.name}'
            embed.description = f'{achievement.description}'
            embed.colour = discord.Colour.blurple()

            embed.set_footer(text=f'Код досягнення: {achievement.fake_id}')

            await self.send_embed(embed)

    async def add_xp(self, amount: int, notify_user: bool = False) -> None:
        self.xp += amount
        await self.save()

        if notify_user:
            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ', url=config.PG_INVITE)
            embed.description = f"Вам нараховано ⚗ **XP** у розмірі `{amount}`"
            embed.colour = discord.Colour.green()

            await self.send_embed(embed)

    # Applies multiple rewards to user
    async def apply_rewards(self, rewards: tuple):
        for r in rewards:
            await r.apply(self)

    async def get_profile_embed(self) -> discord.Embed:
        from src.achievements import Achievements
        member = await self.get_discord_instance()

        embed = DefaultEmbed()
        embed.title = f"**Профіль користувача {member.display_name}**"

        embed.add_field(name='⚖ Рівень', value=f'`{self.level}`')
        embed.add_field(name='⚗ Досвід', value=f'`{self.xp}`')
        embed.add_field(name='🏦 Баланс', value=f'`{self.balance}`')
        embed.add_field(name='🐦 Повідомлення', value=f'`{self.message_count}`')
        embed.add_field(name='⭐ Досягнення', value=f'`{len(self._achievements)}/{len(Achievements)}`')
        embed.add_field(name='🔢 UID', value=f'`#{self.id}`')

        embed.set_thumbnail(url=member.display_avatar.url)

        if member.banner:
            embed.set_image(url=member.banner.url)

        embed.description = f"""
                Прогрес до наступного рівню: `{self.xp}/{self.level_to_xp(self.level + 1)}`
                > ```{self.level} {progress_bar(self.l_tnl_percent)} {self.level + 1}```
                """

        return embed

    async def get_discord_instance(self, preload_guild: discord.Guild = None) -> discord.Member | None:
        if preload_guild is None:
            guild = bot_instance.get_guild(config.PARENT_GUILD)

            if guild is None:
                guild = await bot_instance.fetch_guild(config.PARENT_GUILD)
        else:
            guild = preload_guild

        try:
            # user = await guild.get_or_fetch_member(self.discord_id)
            user = await discord.utils.get_or_fetch(guild, 'member', self.discord_id)
            return user
        except NotFound:
            return None

    async def update_levels(self) -> (int, bool, str | None):
        """
        Update user levels based on XP.

        level - user's level after function execution

        affected - if level was changed - this parameter will be True

        rewards - the thing user achieved with new level
        
        :return: (level: int, affected: bool, rewards: str | None)
        """

        level = self.xp_to_level(self.xp)
        level_gain = level - self.level

        affected = True
        rewards_string = ""

        if level_gain > 0:
            from src.rewards import get_formatted_reward_string, leveled_rewards
            # Iterate through gained levels to add all lost rewards due to some reason.
            member_instance = await self.get_discord_instance()

            if member_instance is None:
                # User left the guild or something happened.
                return level, False, rewards_string or None

            rewards: list = []

            for i in range(self.level, level):
                ext = leveled_rewards.get(i + 1)

                rewards.extend(ext if ext is not None else [])

            for reward in rewards:
                await reward.apply(self)
                rewards_string += f'\n{get_formatted_reward_string(reward)}'

            self.level = level
            await self.save()

        else:
            affected = False

        return level, affected, rewards_string or None
