from random import randint

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general

COMMAND = "fish"


class Fish(Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_random_payout():
        return randint(120, 1200)

    @command(name='fish')
    @cooldown(1, 21600, BucketType.user)
    async def fish(self, ctx):
        """
        Catch some fish and sell them for Coins!
        Buy a fishing rod in the shop today!
        /Payout/ Min: %CURRENCY%120\nMax: %CURRENCY%1200
        /Requirements/ Fishing Rod
        """
        if general.has_failed(COMMAND):
            embed = Embed(
                title=f"{COMMAND.title()}",
                description="You didn't find anything inside this lake. Better luck next time.",
                color=Color.red()
            )
        else:
            payout = self.get_random_payout()
            new_amount = general.check_balance(ctx.guild.id, ctx.author.id, payout)
            if new_amount == 0:
                await ctx.send("You have reached the maximum balance. You cannot make more money.")
                return
            else:
                payout = new_amount

            general.add_money(ctx.guild.id, ctx.author.id, payout)
            currency = general.get_currency(ctx.guild.id)

            embed = Embed(
                title=f"{COMMAND.title()}",
                description="After your fishing trip you sold all fish for %s%s." % (currency, payout),
                color=Color.green()
            )
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Fish(bot))
