from discord.ext.commands import Cog


class OnGuildJoin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild):
        if guild.id in self.bot.BLACKLIST_GUILDS:
            print(f"[BLOCK] Guild: {guild} tried to invite the bot but was blacklisted. (ID: {guild.id})")
            await self.bot.get_guild(guild.id).leave()
        else:
            print(f"[ADD] Guild: {guild} has added the bot. (ID: {guild.id})")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("OnGuildJoin")


def setup(bot):
    bot.add_cog(OnGuildJoin(bot))
