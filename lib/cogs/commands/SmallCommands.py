from discord import Embed, Color
from discord.ext.commands import Cog, command


class SmallCommands(Cog):

    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, title, desc):
        embed = Embed(
            title=title,
            description=desc,
            color=Color.blue()
        )
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @command(name="dashboard", aliases=["website"])
    async def dashboard(self, ctx):
        """Krijg de link om ons dashboard online te bezoeken."""
        embed = self.create_embed(title="Alle Links", desc=f"[**Website**]({self.bot.WEBSITE}) |"
                                                           f"[**Dashboard**]({self.bot.WEBSITE}dashboard/) |"
                                                           f"[**Docs**](https://docs.coinzbot.xyz/) |"
                                                           f"[**Coinzbot Premium**]({self.bot.WEBSITE}buy)")
        await ctx.send(embed=embed)

    @command(name="source", aliases=["sourcecode"])
    async def source(self, ctx):
        """Bekijk de source code online"""
        await ctx.send("**Source Code:** https://github.com/SiebeBaree/Coinz")

    @command(name="invite")
    async def invite(self, ctx):
        """Bekijk de source code online"""
        await ctx.send("**Invite URL:** <https://www.coinzbot.xyz/invite>")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("SmallCommands")


def setup(bot):
    bot.add_cog(SmallCommands(bot))
