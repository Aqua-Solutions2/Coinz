from asyncio import TimeoutError
from random import randint

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, lang, minigames

COMMAND = "higherlower"


class HigherLower(Cog):
    EMOTES = ["🔼", "🔽"]
    STOP = "❌"

    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, ctx, number, multiplier, currency, profit, desc="", color=Color.blue()):
        embed = Embed(description=desc, color=color)
        embed.add_field(name=lang.get_message(ctx.language, 'HIGHLOW_Number'), value=f"{lang.get_message(ctx.language, 'HIGHLOW_NumberWas')} **{number}**", inline=True)
        embed.add_field(name=lang.get_message(ctx.language, 'CMD_Multiplier'), value=f"{multiplier}x", inline=True)
        embed.add_field(name=lang.get_message(ctx.language, 'CMD_Profit'), value=f"{currency}{profit}", inline=True)

        if color == Color.blue():
            embed.add_field(name=lang.get_message(ctx.language, 'HIGHLOW_Continue'), value=f"{self.EMOTES[0]} {lang.get_message(ctx.language, 'HIGHLOW_Higher')}\n"
                                                                                           f"{self.EMOTES[1]} {lang.get_message(ctx.language, 'HIGHLOW_Lower')}\n"
                                                                                           f"{self.STOP} {lang.get_message(ctx.language, 'HIGHLOW_Stop')}", inline=False)
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @command(name="higherlower", aliases=['hl', 'highlow'])
    @cooldown(4, 3600, BucketType.user)
    async def higherlower(self, ctx, bet: int):
        if general.check_status(ctx.guild.id, COMMAND):
            err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet, COMMAND)

            if err_msg is not None:
                await ctx.send(lang.get_message(ctx.language, err_msg))
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
                await message.edit(embed=self.create_embed(ctx, number, multiplier, currency, int(bet * multiplier), lang.get_message(ctx.language, 'MINIGAMES_UserWon'), Color.green()))
            else:
                await message.edit(embed=self.create_embed(ctx, number, multiplier, currency, -bet, lang.get_message(ctx.language, 'MINIGAMES_UserLost'), Color.red()))
        else:
            ctx.command.reset_cooldown(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("HigherLower")


def setup(bot):
    bot.add_cog(HigherLower(bot))
