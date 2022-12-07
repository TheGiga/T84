import discord

from src import DefaultEmbed, T84ApplicationContext
from src.rewards import Reward, leveled_rewards, get_formatted_reward_string


class Rewards(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name='rewards', description='🔮 Список нагород для вказаного рівню.')
    async def rewards(
            self, ctx: T84ApplicationContext, level: discord.Option(int, description='Рівень')
    ):
        rewards: list[Reward] = leveled_rewards.get(level)

        embed = DefaultEmbed()

        if rewards is None:
            embed.title = "???"
            embed.description = "❌ На цьому рівні немає нагород."

            return await ctx.respond(embed=embed)

        embed.title = f"Нагороди {level}-ого рівню"

        desc = ""

        for reward in rewards:
            desc += f"{get_formatted_reward_string(reward)}\n"

        embed.description = desc

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Rewards(bot))
