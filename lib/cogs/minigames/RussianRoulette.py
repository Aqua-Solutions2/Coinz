from asyncio import TimeoutError, sleep
from random import randint

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, minigames

COMMAND = "RussianRoulette"
EMOTES = ["❌", "🔫"]


class RussianRoulette(Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, ctx, desc, currency, bet, multiplier, color=Color.blue()):
        embed = Embed(description=desc, color=color)
        embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
        embed.add_field(name="Profit", value=f"{currency}{int(bet * multiplier)}", inline=True)
        embed.set_author(name=COMMAND, icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @command(name="russian-roulette", aliases=["rroulette", "rr"])
    @cooldown(3, 3600, BucketType.user)
    async def russian_roulette(self, ctx, bet: int):
        """
        Keep risking your life to earn money in Russian Roulette.
        /Example/ `russian-roulette 500`
        """
        err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet)

        if err_msg is not None:
            await ctx.send(err_msg)
            return

        general.remove_money(ctx.guild.id, ctx.author.id, bet)

        bullet = randint(1, 6)
        hole = 1
        multiplier = 1.0

        currency = general.get_currency(ctx.guild.id)
        message = await ctx.send(embed=self.create_embed(ctx, "You are now playing Russian Roulette. There is 1 bullet in this gun.\nTry not to get killed.", currency, bet, multiplier))
        await sleep(2)
        await message.add_reaction(EMOTES[0])
        await message.add_reaction(EMOTES[1])

        def check(reactie, gebruiker):
            return gebruiker == ctx.author and str(reactie.emoji) in EMOTES

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=10)
                emote = reaction.emoji

                await message.remove_reaction(emoji=emote, member=ctx.author)

                if emote == EMOTES[0]:
                    general.add_money(ctx.guild.id, ctx.author.id, int(bet * multiplier))
                    await message.edit(embed=self.create_embed(ctx, "You quit the game.", currency, bet, multiplier, Color.green()))
                    await message.clear_reactions()
                    break
                else:
                    hole += 1
                    multiplier = round(multiplier + 0.5, 1)
                    await message.edit(embed=self.create_embed(ctx, "Pulling the trigger...", currency, bet, multiplier))
                    await sleep(1.5)

                if hole == bullet:
                    await message.edit(embed=self.create_embed(ctx, ":skull_crossbones: You died.", currency, bet, multiplier, Color.red()))
                    await message.clear_reactions()
                    await message.add_reaction("☠️")
                    break
                else:
                    await message.edit(embed=self.create_embed(ctx, "You survived! Do you want to play a next round?\nPress :gun:, if you want to quit press :x:.", currency, bet, multiplier))
            except TimeoutError:
                embed = Embed(description="I got no responds. The command is cancelled.", color=Color.red())
                embed.set_author(name=COMMAND, icon_url=f"{ctx.author.avatar_url}")
                embed.set_footer(text=self.bot.FOOTER)
                await message.edit(embed=embed)
                break

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND)


def setup(bot):
    bot.add_cog(RussianRoulette(bot))
