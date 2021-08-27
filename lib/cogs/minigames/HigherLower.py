from asyncio import TimeoutError
from random import randint

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, minigames

COMMAND = "higherlower"


class HigherLower(Cog):
    EMOTES = ["🔼", "🔽"]
    STOP = "❌"

    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, ctx, number, multiplier, currency, profit, desc="", color=Color.blue()):
        embed = Embed(description=desc, color=color)
        embed.add_field(name="Number", value=f"The number was **{number}**", inline=True)
        embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
        embed.add_field(name="Profit", value=f"{currency}{profit}", inline=True)

        if color == Color.blue():
            embed.add_field(name="Continue", value=f"{self.EMOTES[0]} To guess the next number is higher.\n"
                                                   f"{self.EMOTES[1]} To guess the next number is lower.\n"
                                                   f"{self.STOP} To stop and collect.", inline=False)
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @command(name="higherlower", aliases=['hl', 'highlow'])
    @cooldown(4, 3600, BucketType.user)
    async def higherlower(self, ctx, bet: int):
        """
        Will the next number be higher or lower than the previous one?
        /Examples/ `higherlower 500`
        """
        err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet)

        if err_msg is not None:
            await ctx.send(err_msg)
            return

        currency = general.get_currency(ctx.guild.id)
        general.remove_money(ctx.guild.id, ctx.author.id, bet)

        multiplier = 1
        user_won = False
        ronde = 0
        number = 5
        message = await ctx.send(embed=self.create_embed(ctx, number, multiplier, currency, int(bet * multiplier)))

        for emote in self.EMOTES:
            await message.add_reaction(emote)

        def check(reactie, gebruiker):
            return gebruiker == ctx.author and str(reactie.emoji) in self.EMOTES or gebruiker == ctx.author and str(reactie.emoji) == self.STOP

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                emote = reaction.emoji

                if ronde == 1:
                    await message.add_reaction(self.STOP)

                next_number = randint(1, 10)
                while next_number == number:
                    next_number = randint(1, 10)

                if emote == self.EMOTES[0]:
                    user_won = True if next_number > number else False
                elif emote == self.EMOTES[1]:
                    user_won = True if next_number < number else False
                else:
                    break

                await message.remove_reaction(emote, ctx.author)
                number = next_number

                if user_won:
                    multiplier *= 2
                else:
                    break

                await message.edit(embed=self.create_embed(ctx, number, multiplier, currency, int(bet * multiplier)))
            except TimeoutError:
                break
            ronde += 1

        await message.clear_reactions()

        if user_won:
            general.add_money(ctx.guild.id, ctx.author.id, int(bet * multiplier))
            await message.edit(embed=self.create_embed(ctx, number, multiplier, currency, int(bet * multiplier), "You Won", Color.green()))
        else:
            await message.edit(embed=self.create_embed(ctx, number, multiplier, currency, -bet, "You Lost", Color.red()))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("HigherLower")


def setup(bot):
    bot.add_cog(HigherLower(bot))
