from asyncio import TimeoutError
from random import randint

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, minigames

COMMAND = "crash"


class Crash(Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, ctx, multiplier, currency, profit, color=Color.blue()):
        embed = Embed(color=color)
        embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
        embed.add_field(name="Profit", value=f"{currency}{profit}", inline=True)
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @command(name="crash", aliases=["market-crash"])
    @cooldown(3, 3600, BucketType.user)
    async def crash(self, ctx, bet: int):
        """
        Are you fast enough to stop before it crashes?
        /Examples/ `crash 500`
        """
        err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet, COMMAND)

        if err_msg is not None:
            await ctx.send(err_msg)
            return

        currency = general.get_currency(ctx.guild.id)
        general.remove_money(ctx.guild.id, ctx.author.id, bet)

        rate = 1.0
        profit = bet
        message = await ctx.send("React with :x: to stop.", embed=self.create_embed(ctx, rate, currency, profit))
        await message.add_reaction("❌")

        def check(reactie, gebruiker):
            return gebruiker == ctx.author and str(reactie.emoji) in ["❌"]

        while True:
            try:
                await self.bot.wait_for('reaction_add', timeout=1.2, check=check)
                general.add_money(ctx.guild.id, ctx.author.id, profit)
                await message.edit(content="", embed=self.create_embed(ctx, rate, currency, profit, Color.green()))
                await message.clear_reaction("❌")
                break
            except TimeoutError:
                if randint(1, 12) == 8:
                    await message.edit(content="", embed=self.create_embed(ctx, rate, currency, -bet, Color.red()))
                    await message.clear_reaction("❌")
                    break
                else:
                    rate = round(rate + 0.2, 1)
                    profit = int(bet * rate)
                    await message.edit(embed=self.create_embed(ctx, rate, currency, profit))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Crash(bot))
