from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown
from lib.checks import general, lang

COMMAND = "fish"


class Fish(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='fish')
    @cooldown(1, 21600, BucketType.user)
    async def fish(self, ctx):
        if general.check_status(ctx.guild.id, COMMAND):
            if general.has_failed(ctx.guild.id, COMMAND):
                embed = Embed(
                    title=f"{COMMAND.title()}",
                    description=lang.get_message(ctx.language, "FISH_NoMoney"),
                    color=Color.red()
                )
            else:
                payout = general.get_payout(ctx.guild.id, COMMAND)

                new_amount = general.check_balance(ctx.guild.id, ctx.author.id, payout)
                if new_amount == 0:
                    await ctx.send(lang.get_message(ctx.language, 'CMD_ExceedBalLimitAuthor'))
                    return
                else:
                    payout = new_amount

                general.add_money(ctx.guild.id, ctx.author.id, payout)
                currency = general.get_currency(ctx.guild.id)

                embed = Embed(
                    title=f"{COMMAND.title()}",
                    description=lang.get_message(ctx.language, "FISH_GetMoney") % (currency, payout),
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
    bot.add_cog(Fish(bot))
