import time
from datetime import datetime
from platform import python_version

from discord import Embed, __version__, Color
from discord.ext.commands import Cog, command, cooldown, BucketType
from psutil import Process, virtual_memory

start_time = time.time()


class Stats(Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def calculate_uptime():
        current_time = time.time()
        uptime = current_time - start_time

        if uptime >= 86400:
            uptime = time.strftime('%-dd %-Hu %-Mm %-Ss', time.gmtime(uptime))
        else:
            uptime = time.strftime('%-Hu %-Mm %-Ss', time.gmtime(uptime))

        return uptime

    @command(name="ping", aliases=["uptime"])
    @cooldown(1, 5, BucketType.user)
    async def ping(self, ctx):
        """Get the latency in milliseconds and the uptime of the bot."""
        responds_time_start = time.time()
        message = await ctx.send(f":radio_button: Calculating...")
        responds_time_end = time.time()
        await message.edit(content=f":ping_pong: **Ping:** {self.bot.get_shard(ctx.guild.shard_id).latency * 1000:,.0f} ms\n"
                                   f":speech_balloon: **Responds Time:** {(responds_time_end - responds_time_start) * 1000:,.0f} ms\n"
                                   f":white_check_mark: **Uptime:** {self.calculate_uptime()}")

    @command(name="stats", aliases=["statistics"])
    @cooldown(1, 10, BucketType.user)
    async def stats(self, ctx):
        """Get information about the bot."""
        embed = Embed(
            title="Bot Statistics",
            color=Color.blue(),
            timestamp=datetime.utcnow()
        )

        proc = Process()
        with proc.oneshot():
            mem_total = virtual_memory().total / (1024**2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        fields = [("Python Version", f"{python_version()}", True),
                  ("Discord.py Version", f"{__version__}", True),
                  ("Uptime", f"{self.calculate_uptime()}", True),
                  ("Shard", f"{ctx.guild.shard_id + 1}/{self.bot.shard_count}", True),
                  ("Memory Usage", f"{mem_usage:,.0f} / {mem_total:,.0f} MB ({mem_of_total:,.0f}%)", True),
                  ("Total Users", f"{sum([len(guild.members) for guild in self.bot.guilds])}", True),
                  ("Total Guilds", f"{len(self.bot.guilds)}", True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=self.bot.FOOTER)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Utility")


def setup(bot):
    bot.add_cog(Stats(bot))
