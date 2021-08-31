from discord.ext.commands import command, Cog, BucketType, cooldown


class Shop(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='shop', aliases=["buy"])
    @cooldown(1, 5, BucketType.user)
    async def shop(self, ctx, *option):
        """
        Buy stuff from the shop to make even more money.\n**(SOON)** Pets can be bought with the animals command.
        /Subcommands/ `list` - View every item in the shop.\n`<item>` - Buy a item from the shop.
        /Examples/ `shop list`\n`shop fishing rod`
        """
        pass

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Shop")


def setup(bot):
    bot.add_cog(Shop(bot))
