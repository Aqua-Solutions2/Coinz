from asyncio import TimeoutError

from discord.ext.commands import Cog, command, cooldown, BucketType

from lib.checks import lang
from lib.db import db

emote = '✅'


class ResetBalance(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="reset-account", aliases=["resetaccount", "resetacc", "racc"])
    @cooldown(1, 10, BucketType.user)
    async def reset_account(self, ctx):
        message = await ctx.send(lang.get_message(ctx.language, 'RESET_Account') % emote)
        await message.add_reaction(emote)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == emote

        try:
            await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
            await ctx.send(lang.get_message(ctx.language, 'RESET_AccountSuccess'))
            db.execute("DELETE FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
        except TimeoutError:
            await ctx.send(lang.get_message(ctx.language, 'CMD_NoResponds'))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("ResetBalance")


def setup(bot):
    bot.add_cog(ResetBalance(bot))
