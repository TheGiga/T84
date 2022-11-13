from math import sqrt, floor

import discord
from discord import NotFound
from tortoise import fields
from tortoise.models import Model

import config
from src import bot_instance, DefaultEmbed, progress_bar


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

    @property
    def xp_tnl(self) -> int:
        """
        :return: INT: Amount of XP needed to reach next level.
        """
        xp_nl = self.level_to_xp(self.level + 1)
        xp_tnl = xp_nl - self.xp

        return xp_tnl

    async def add_balance(self, amount: int, notify_user: bool = False) -> None:
        self.balance += amount
        await self.save()

        if notify_user:
            discord_instance = await self.get_discord_instance()

            if not discord_instance.can_send(discord.Message, discord.Embed):
                return

            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ', url=config.PG_INVITE)
            embed.description = f"Вам нараховано 🪙 **Баланс** у розмірі `{amount}`"
            embed.colour = discord.Colour.gold()

            try:
                await discord_instance.send(embed=embed)
            except discord.Forbidden:
                pass

    async def add_achievement(
            self, achievement, notify_user: bool = False
    ) -> None:
        current_achievements = list(self.achievements)
        if achievement.identifier in current_achievements:
            return

        current_achievements.append(achievement.identifier)
        self.achievements = current_achievements
        await self.save()

        if notify_user:
            discord_instance = await self.get_discord_instance()

            if not discord_instance.can_send(discord.Message, discord.Embed):
                return

            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ | Досягнення', url=config.PG_INVITE)
            embed.title = f'\🔵 {achievement.text}'
            embed.description = f'{achievement.long_text}'
            embed.colour = discord.Colour.blurple()

            embed.set_footer(text=f'Код досягнення: {achievement.identifier}')

            try:
                await discord_instance.send(embed=embed)
            except discord.Forbidden:
                pass

    async def add_xp(self, amount: int, notify_user: bool = False) -> None:
        self.xp += amount
        await self.save()

        if notify_user:
            discord_instance = await self.get_discord_instance()

            if not discord_instance.can_send(discord.Message, discord.Embed):
                return

            embed = DefaultEmbed()

            embed.set_author(name='ДТВУ', url=config.PG_INVITE)
            embed.description = f"Вам нараховано 🎈 **XP** у розмірі `{amount}`"
            embed.colour = discord.Colour.green()

            try:
                await discord_instance.send(embed=embed)
            except discord.Forbidden:
                pass

    async def get_profile_embed(self) -> discord.Embed:
        member = await self.get_discord_instance()

        embed = DefaultEmbed()
        embed.title = f"**Профіль користувача {member.display_name}**"

        embed.add_field(name='⚖ Рівень', value=f'`{self.level}`')
        embed.add_field(name='🎈 Досвід', value=f'`{self.xp}`')
        embed.add_field(name='🪙 Баланс', value=f'`{self.balance}`')

        embed.set_thumbnail(url=member.display_avatar.url)

        xp_to_new_level = self.xp - self.level_to_xp(self.level)
        xp_new_level = self.level_to_xp(self.level + 1) - self.level_to_xp(self.level)

        percent = round((xp_to_new_level / xp_new_level) * 100)

        embed.description = f"""
                Прогрес до наступного рівню: `{self.xp}/{self.level_to_xp(self.level + 1)}`
                > ```{self.level} {progress_bar(percent)} {self.level + 1}```
                """

        # Placeholder image to make embed have the same width everytime
        embed.set_image(url="https://i.imgur.com/WozcNGD.png")

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
        rewards = "\n"

        if level_gain > 0:
            from src.rewards import Reward, get_formatted_reward_string
            # Iterate through gained levels to add all lost rewards due to some reason.
            member_instance = await self.get_discord_instance(preload_guild=guild)

            if member_instance is None:
                # User left the guild or something happened.
                return level, False, rewards

            awards: list[Reward] = []

            for i in range(self.level, level):
                ext = config.leveled_rewards.get(i + 1)

                awards.extend(ext if ext is not None else [])

            for award in awards:
                reward_value = await award.apply_reward(self)
                rewards += f'{get_formatted_reward_string(reward_value)}\n'

        else:
            affected = False

        self.level = level
        await self.save()

        rewards = rewards if len(rewards) > 0 else None
        return level, affected, rewards
