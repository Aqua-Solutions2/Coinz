from discord.ext.commands import Cog, command, is_owner


class OwnerCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="kill", aliases=["shutdown", "disconnect", "stop"])
    @is_owner()
    async def kill_cmd(self, ctx):
        """HIDDEN"""
        await ctx.send("Closing connection to the Discord API. Bye...")
        await self.bot.close()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("OwnerOnly")


def setup(bot):
    bot.add_cog(OwnerCommands(bot))
