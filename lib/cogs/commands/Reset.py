from asyncio import TimeoutError

from discord.ext.commands import Cog, command, cooldown, BucketType

from lib.checks import lang
from lib.db import db


class ResetCmd(Cog):
    VALID_MESSAGES = ['all', 'config', 'userdata']

    def __init__(self, bot):
        self.bot = bot

    @command(name="reset")
    @cooldown(1, 60, BucketType.guild)
    async def reset_(self, ctx):
        """Reset specific data from your server."""
        await ctx.send(lang.get_message(ctx.language, 'RESET_General') % ", ".join(self.VALID_MESSAGES))

        def check(m):
            return m.author == ctx.author and m.content.lower() in self.VALID_MESSAGES

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=20)
            option = msg.content.lower()

            if option == self.VALID_MESSAGES[0]:
                for table in self.bot.TABLES:
                    db.execute(f"DELETE FROM {table} WHERE GuildID = %s", ctx.guild.id)
                await ctx.send(lang.get_message(ctx.language, 'RESET_All'))
            elif option == self.VALID_MESSAGES[1]:
                db.execute(f"DELETE FROM guildPayouts WHERE GuildID = %s", ctx.guild.id)
                db.execute(f"DELETE FROM guildWorkPayouts WHERE GuildID = %s", ctx.guild.id)
                db.execute(f"DELETE FROM guilds WHERE GuildID = %s", ctx.guild.id)
                await ctx.send(lang.get_message(ctx.language, 'RESET_Config'))
            else:
                db.execute(f"DELETE FROM userData WHERE GuildID = %s", ctx.guild.id)
                await ctx.send(lang.get_message(ctx.language, 'RESET_UserData'))
        except TimeoutError:
            await ctx.send(lang.get_message(ctx.language, 'CMD_NoResponds'))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Reset")


def setup(bot):
    bot.add_cog(ResetCmd(bot))
