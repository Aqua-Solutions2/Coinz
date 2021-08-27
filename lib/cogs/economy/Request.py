from discord import Embed, Color, Member
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general


class Request(Cog):
    MIN = 1
    MAX = 1000000000000

    def __init__(self, bot):
        self.bot = bot

    @command(name='request', aliases=["bill"])
    @cooldown(1, 1800, BucketType.user)
    async def request(self, ctx, member: Member, amount: int):
        """Request money from someone."""
        if self.MAX >= amount >= self.MIN:
            currency = general.get_currency(ctx.guild.id)
            message_url = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}"
            embed = Embed(
                description="%s has requested money from you.\n\n**Amount:** %s%s\n**Server:** %s\n**Message:** [Go To Message](%s)" % (ctx.author, currency, amount, ctx.guild, message_url),
                color=Color.blue()
            )
            embed.set_author(name="Request", icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text=self.bot.FOOTER)

            try:
                await member.send(embed=embed)
                await ctx.send("%s, %s has requested money from you.\n**Amount:** %s%s" % (member, ctx.author, currency, amount))
            except Exception:
                await ctx.send("%s, %s has requested money from you.\n**Amount:** %s%s" % (member.mention, ctx.author, currency, amount))
        else:
            await ctx.send("You have to give a valid number between %s and %s." % (self.MIN, self.MAX))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Request")


def setup(bot):
    bot.add_cog(Request(bot))
