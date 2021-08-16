from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, lang

COMMAND = "crime"


class Crime(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    @cooldown(1, 43200, BucketType.user)
    async def crime(self, ctx):
        """
        Want to live a live of crime?
        Take your chances to win a lot of money.
        /Payout/ Min: %CURRENCY%%MIN%\nMax: %CURRENCY%%MAX%
        /Risk/ %FAIL% to fail.
        """
        if general.check_status(ctx.guild.id, COMMAND):
            payout = general.get_payout(ctx.guild.id, COMMAND)

            new_amount = general.check_balance(ctx.guild.id, ctx.author.id, payout)
            if new_amount == 0:
                await ctx.send(lang.get_message(ctx.language, 'CMD_ExceedBalLimitAuthor'))
                return
            else:
                payout = new_amount

            if general.has_failed(ctx.guild.id, COMMAND):
                payout = int((payout / 100) * 75)
                answer = general.get_random_sentence(f'{ctx.language.lower()}_crime_fail', ctx.guild.id, payout)
                general.remove_money(ctx.guild.id, ctx.author.id, payout)

                embed = Embed(
                    title=f"{COMMAND.title()}",
                    description=f"{answer}",
                    color=Color.red()
                )
            else:
                answer = general.get_random_sentence(f'{ctx.language.lower()}_crime_success', ctx.guild.id, payout)
                general.add_money(ctx.guild.id, ctx.author.id, payout)

                embed = Embed(
                    title=f"{COMMAND.title()}",
                    description=f"{answer}",
                    color=Color.green()
                )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text=self.bot.FOOTER)
            await ctx.send(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Crime(bot))
