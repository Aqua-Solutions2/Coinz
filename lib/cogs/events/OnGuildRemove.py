from discord.ext.commands import Cog
from lib.db import db


class OnGuildRemove(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"[DEL] Guild: {guild} has removed the bot. (ID: {guild.id})")

        for table in self.bot.TABLES:
            db.execute(f"DELETE FROM {table} WHERE GuildID = %s", guild.id)
        db.commit()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("OnGuildRemove")


def setup(bot):
    bot.add_cog(OnGuildRemove(bot))
