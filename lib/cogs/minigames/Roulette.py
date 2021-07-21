from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown
from lib.checks import general, lang, minigames
from random import randint
from asyncio import sleep

COMMAND = "roulette"


class Roulette(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="roulette")
    @cooldown(2, 3600, BucketType.user)
    async def roulette(self, ctx, bet: int, space):
        if general.check_status(ctx.guild.id, COMMAND):
            err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet, COMMAND)

            if err_msg is not None:
                await ctx.send(lang.get_message(ctx.language, err_msg))
                return

            number = randint(0, 36)
            red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
            space = space.lower()
            money_won = 0

            try:
                space = int(space)
                if 0 <= space <= 36:
                    if space == number:
                        money_won = 36
                else:
                    await ctx.send(lang.get_message(ctx.language, 'ERR_InvalidArguments'))
                    return
            except ValueError:
                if space == "red":
                    if number in red_numbers:
                        money_won = 2
                elif space == "black":
                    if number in black_numbers:
                        money_won = 2
                elif space == "odd":
                    if number % 2 == 1:
                        money_won = 2
                elif space == "even":
                    if number % 2 == 0:
                        money_won = 2
                elif space == "1st" or space == "first":
                    if number in [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]:
                        money_won = 3
                elif space == "2nd" or space == "second":
                    if number in [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]:
                        money_won = 3
                elif space == "3rd" or space == "third":
                    if number in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]:
                        money_won = 3
                elif space == "1-12":
                    if 1 <= number <= 12:
                        money_won = 3
                elif space == "13-24":
                    if 13 <= number <= 24:
                        money_won = 3
                elif space == "25-36":
                    if 25 <= number <= 36:
                        money_won = 3
                elif space == "1-18":
                    if 1 <= number <= 18:
                        money_won = 2
                elif space == "19-36":
                    if 19 <= number <= 36:
                        money_won = 2
                else:
                    await ctx.send(lang.get_message(ctx.language, 'ERR_InvalidArguments'))
                    return

            if number in red_numbers:
                ball = f"red {number}"
            elif number in black_numbers:
                ball = f"black {number}"
            else:
                ball = number

            general.remove_money(ctx.guild.id, ctx.author.id, bet)
            embed = Embed(description=lang.get_message(ctx.language, 'ROULETTE_Rolling'), color=Color.blue())
            embed.set_image(url="https://media2.giphy.com/media/26uf2YTgF5upXUTm0/giphy.gif")
            embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text=self.bot.FOOTER)
            message = await ctx.send(embed=embed)
            await sleep(3)

            currency = general.get_currency(ctx.guild.id)
            if money_won != 0:
                money_won = round(bet * money_won)
                general.add_money(ctx.guild.id, ctx.author.id, money_won-bet)
                embed = Embed(description=f"{lang.get_message(ctx.language, 'ROULETTE_BallLandedOn') % ball}\n{lang.get_message(ctx.language, 'MINIGAMES_UserWon')} {currency}{money_won}!", color=Color.green())
            else:
                embed = Embed(description=f"{lang.get_message(ctx.language, 'ROULETTE_BallLandedOn') % ball}\n{lang.get_message(ctx.language, 'MINIGAMES_UserLost')} {currency}{bet}!", color=Color.red())
            embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text=self.bot.FOOTER)
            await message.edit(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Roulette(bot))
