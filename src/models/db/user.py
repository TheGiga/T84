import datetime
import logging
from math import sqrt, floor

import discord
from discord import NotFound
from tortoise import fields
from tortoise.models import Model

import config
from src import bot_instance, DefaultEmbed
from src.base_types import Unique
from src.utils import progress_bar, boolean_emoji

from typing import TYPE_CHECKING
from .bp import BattlePassModel
from ...bot import T84

if TYPE_CHECKING:
    from src.achievements import Achievement
    from src.models import XPBooster


class User(Model):
    # Basic

    id = fields.IntField(pk=True)
    discord_id = fields.IntField()

    # Variables

    beta = fields.BooleanField(default=False)

    # Data

    xp = fields.IntField(default=0)
    level = fields.IntField(default=0)
    balance = fields.IntField(default=0)
    premium_balance = fields.IntField(default=0)

    # Storage-able

    _achievements = fields.JSONField(source_field="achievements", default=[])
    _inventory = fields.JSONField(source_field="inventory", default=[]) # might be unnecessary
    _roles = fields.JSONField(source_field="roles", default=[])

    # Other
    xp_multiplier = fields.FloatField(default=1.0)

    def __int__(self):
        return self.discord_id

    def __str__(self):
        return f"User({self.id})"

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
    def inventory(self) -> list[Unique]:
        return [
            Unique.get_from_key(key)
            for key in self._inventory
        ]

    @property
    def achievements(self) -> list['Achievement']:
        return [
            Unique.get_from_key(key)
            for key in self._achievements
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


    async def get_stored_roles(self) -> list[discord.Role]:
        discord_instance = await self.get_discord_instance()
        guild = discord_instance.guild

        to_return = []

        for role_id in self._roles:
            role = guild.get_role(role_id)

            if role is None:
                await T84.send_critical_log(
                    f'User.get_stored_roles | The role {role_id} appears to be None.', level=logging.ERROR
                )
                continue

            to_return.append(role)

        return to_return

    async def set_stored_roles(self, value: list[discord.Role] | list[int]):
        def check(x) -> int:
            if type(x) is int:
                return x

            return x.id

        to_store = list(map(lambda x: check(x), value))

        self._roles = to_store
        await self.save()

    async def add_stored_role(self, value: int | discord.Role):
        if type(value) is discord.Role:
            value = value.id

        if value in self._roles:
            return

        self._roles.append(value)
        await self.save()

    async def apply_xp_booster(self, power: float, duration: datetime.timedelta) -> 'XPBooster':
        from src.models import XPBooster
        valid_until = datetime.datetime.utcnow() + duration
        booster = await XPBooster.create(user_id=self.id, power=power, valid_until=valid_until)
        await booster.apply()

        return booster

    async def get_battlepass_data(self, season: int = config.CURRENT_BP_SEASON) -> 'BattlePassModel':
        """Users battlepass data"""

        bp_data, _ = await BattlePassModel.get_or_create(user_id=self.id)

        return bp_data

    async def send(self, embed: discord.Embed = None, content: str = None, view: discord.ui.View = None) -> None:
        if not embed and not content and not view:
            return

        discord_instance = await self.get_discord_instance()

        try:
            await discord_instance.send(content=content, embed=embed, view=view)
        except discord.HTTPException:
            msg = f"Couldn't send message to {discord_instance.id}, most likely due to closed DM's."
            logging.info(msg)

    async def add_inventory_item(self, item: Unique) -> None:
        """
        Note: Item should be an instance of src.base_types.Inventoriable

        :param item: Unique (src.base_types.Unique) item
        :return: None
        """
        inventory = list(self._inventory)

        if item.key in inventory:
            return

        if not issubclass(item.__class__, Unique):
            return

        inventory.append(item.key)
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
                                f"\n{additional_message if additional_message else ''}"
            embed.colour = discord.Colour.gold()
            try:
                await self.send(embed)
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
                await self.send(embed)
            except discord.HTTPException:
                pass

    async def add_achievement(
            self, achievement: 'Achievement', notify_user: bool = False
    ) -> None:
        current_achievements = list(self._achievements)
        if achievement.key in current_achievements:
            return

        current_achievements.append(achievement.key)
        self._achievements = current_achievements
        await self.save()

        if notify_user:
            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ | Досягнення', url=config.PG_INVITE)
            embed.title = f'🔹 {achievement.name}'
            embed.description = f'{achievement.description}'
            embed.colour = discord.Colour.blurple()

            embed.set_footer(text=f'Код досягнення: {achievement.key}')

            await self.send(embed=embed)

    async def add_xp(self, amount: int, notify_user: bool = False) -> None:
        self.xp += amount
        await self.save()

        if notify_user:
            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ', url=config.PG_INVITE)
            embed.description = f"Вам нараховано ⚗ **XP** у розмірі `{amount}`"
            embed.colour = discord.Colour.green()

            await self.send(embed)

    # Applies multiple rewards to user
    # Edit: i don't fucking know why i implemented this like, well, that
    async def apply_rewards(self, rewards: tuple):
        for r in rewards:
            await r.apply(self)

    async def get_profile_embed(self) -> discord.Embed:
        from src.achievements import Achievements
        member = await self.get_discord_instance()
        bp = await self.get_battlepass_data()

        embed = DefaultEmbed()
        embed.title = f"**Профіль користувача {member.display_name}**"

        embed.add_field(name='⚖️ Рівень', value=f'`{self.level}`')
        embed.add_field(name='⚗️ Досвід', value=f'`{self.xp} ({self.xp_multiplier}x)`')
        embed.add_field(name='🏦 Баланс', value=f'`{self.balance}`')
        embed.add_field(name="♾️ Рівень BP", value=f'`{bp.level}`')
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

    async def get_battlepass_embed(self, season: int = config.CURRENT_BP_SEASON) -> discord.Embed:
        from src import BattlePassLevels

        bp = await self.get_battlepass_data(season=season)
        embed = DefaultEmbed()

        if bp.premium:
            embed.colour = discord.Colour.blurple()

        next_rewards = BattlePassLevels.get_by_level(bp.level + 1)

        if not next_rewards:
            next_rewards = None
        elif next_rewards.paid and not bp.premium:
            next_rewards = None

        percent = (bp.xp / ((bp.level + 1) * config.BP_XP_PER_LEVEL)) * 100
        progress = progress_bar(percent)

        embed.title = f'📔 Баттл-Пасс сезон #{config.CURRENT_BP_SEASON}'

        embed.description = f"""        
        > ```{bp.level} {progress} {bp.level+1}``` Прогрес до наступного рівню: `{bp.xp}/{(bp.level+1) 
                                                                                          * config.BP_XP_PER_LEVEL}`
        
        {'⭐' if next_rewards.paid else '🔹'} **Нагороди наступного рівню:**
        {next_rewards if next_rewards else '*Нагороди наступного рівню тільки преміальні*'}
        """

        embed.add_field(name="🔘 Досвід BP", value=f'`{bp.xp}`')
        embed.add_field(name="♾️ Рівень BP", value=f'`{bp.level}`')
        embed.add_field(name="💎 Преміум", value=boolean_emoji(bp.premium))

        embed.set_thumbnail(url='https://i.imgur.com/BapZMjf.png')

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

    async def timeout(self, reason: str, duration: datetime.timedelta, moderator: discord.Member) -> None:
        """
        :param reason: timeout reason
        :param duration: duration of the timeout
        :param moderator: User who gave out the timeout
        :return None
        """
        discord_instance = await self.get_discord_instance()

        await discord_instance.timeout_for(duration, reason=reason)
        await T84.send_critical_log(
            f"Користувачу {discord_instance.mention} `({discord_instance.id})` було видано тайм-аут модератором "
            f"{moderator} `({moderator.id})` за причиною: `{reason}`", level=logging.INFO
        )

        embed = DefaultEmbed()
        embed.title = "⚠️ Вам було видано тайм-аут!"
        embed.description = f'🚔 Модератор {moderator.mention} видав вам тайм-аут за причиною: ' \
                            f'```glsl\n# {reason}```\n' \
                            f'⚖️ Оскаржити покарання можна у каналі <#{config.APPEAL_CHANNEL}>'

        await self.send(embed=embed)
