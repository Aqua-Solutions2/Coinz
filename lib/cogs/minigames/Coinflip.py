from asyncio import TimeoutError
from random import choice

from discord import Embed, Color, Member
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, minigames

COMMAND = "coinflip"


class Coinflip(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="coinflip", aliases=["cf"])
    @cooldown(2, 3600, BucketType.user)
    async def coinflip(self, ctx, member: Member, bet: int, side: str):
        """
        Flip a coin and let fait decide.
        /Examples/ `coinflip Siebe 500 head`\n`coinflip Siebe 500 tails`
        """
        err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet, member.id)

        if err_msg is not None:
            await ctx.send(err_msg)
            return

        options = ["head", "tails"]
        side = side.lower()
        if side not in options:
            return

        currency = general.get_currency(ctx.guild.id)
        play_token = minigames.create_token()

        embed = Embed(
            description="%s has challenged %s in a game of %s.\n%s, if you type `%s` in chat the game will start.\nYou have 60 seconds to decide." % (ctx.author, member, COMMAND, member.display_name, play_token),
            color=Color.blue()
        )
        embed.add_field(name="Bet", value=f"{currency}{bet}", inline=True)
        embed.add_field(name=f"{ctx.author}", value=f"{side}", inline=True)
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        message_embed = await ctx.send(f"{member.mention}", embed=embed)

        def check(message):
            return message.author.id == member.id and message.channel == ctx.channel and message.content.lower() == f"{play_token.lower()}"

        try:
            await self.bot.wait_for('message', check=check, timeout=60)

            general.create_row(ctx.guild.id, member.id)
            err_msg = minigames.general_checks(ctx.guild.id, member.id, bet)

            if err_msg is not None:
                await ctx.send(err_msg)
                return

            general.remove_money(ctx.guild.id, ctx.author.id, bet)
            general.remove_money(ctx.guild.id, member.id, bet)

            winner = ctx.author if side == choice(options) else member
            general.add_money(ctx.guild.id, winner.id, bet * 2)
            embed = Embed(description="%s won %s%s!" % (winner.mention, currency, bet * 2), color=Color.green())
            embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text=self.bot.FOOTER)
            await message_embed.edit(content="", embed=embed)
        except TimeoutError:
            await ctx.send("I got no responds. The command is cancelled.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Coinflip(bot))
