from discord.ext.commands import Cog, command, is_owner
from glob import glob


class CoreFile(Cog):
    COG_FOLDERS = [path.split("/")[-1] for path in glob(f"./lib/cogs/*") if not path.endswith('__pycache__')]
    COGS = [f'{folder}.{path.split("/")[-1][:-3]}' for folder in COG_FOLDERS for path in glob(f"./lib/cogs/{folder}/*.py")]

    def __init__(self, bot):
        self.bot = bot

    @command(name="load")
    @is_owner()
    async def load(self, ctx, cog_name: str):
        if cog_name == "*":
            self.bot.setup()
        else:
            for folder in self.COG_FOLDERS:
                try:
                    self.bot.load_extension(f'lib.cogs.{folder}.{cog_name}')
                    print(f"[{self.bot.user.name}] Cog {cog_name}: Manually Loaded by {ctx.author}")
                    await ctx.send(f"File {cog_name}.py loaded.")
                    return
                except Exception:
                    pass

            print(f"[{self.bot.user.name}] Cog {cog_name}: Error occured while trying to load cog.")
            await ctx.send(f"File {cog_name}.py could not be found, please try again.")

    @command(name="reload")
    @is_owner()
    async def reload(self, ctx, cog_name: str):
        if cog_name == "*":
            for cog in self.COGS:
                try:
                    self.bot.unload_extension(f'lib.cogs.{cog}')
                    self.bot.load_extension(f'lib.cogs.{cog}')
                    print(f"[{self.bot.user.name}] Cog {cog_name}: Manually Reloaded by {ctx.author}")
                except Exception:
                    pass
            await ctx.send(f"All cogs are reloaded.")
        else:
            for folder in self.COG_FOLDERS:
                try:
                    self.bot.unload_extension(f'lib.cogs.{folder}.{cog_name}')
                    self.bot.load_extension(f'lib.cogs.{folder}.{cog_name}')
                    print(f"[{self.bot.user.name}] Cog {cog_name}: Manually Reloaded by {ctx.author}")
                    await ctx.send(f"File {cog_name}.py reloaded.")
                    return
                except Exception:
                    pass

            print(f"[{self.bot.user.name}] Cog {cog_name}: Error occured while trying to load cog.")
            await ctx.send(f"File {cog_name}.py could not be found, please try again.")

    @command(name="unload")
    @is_owner()
    async def unload(self, ctx, cog_name: str):
        if cog_name == "*":
            for cog in self.COGS:
                try:
                    self.bot.unload_extension(f'lib.cogs.{cog}')
                    print(f"[{self.bot.user.name}] Cog {cog_name}: Manually Unloaded by {ctx.author}")
                except Exception:
                    pass
            await ctx.send(f"All cogs are unloaded.")
        else:
            for folder in self.COG_FOLDERS:
                try:
                    self.bot.unload_extension(f'lib.cogs.{folder}.{cog_name}')
                    print(f"[{self.bot.user.name}] Cog {cog_name}: Manually Unloaded by {ctx.author}")
                    await ctx.send(f"File {cog_name}.py unloaded.")
                    return
                except Exception:
                    pass

            print(f"[{self.bot.user.name}] Cog {cog_name}: Error occured while trying to load cog.")
            await ctx.send(f"File {cog_name}.py could not be found, please try again.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Core")


def setup(bot):
    bot.add_cog(CoreFile(bot))
