from discord import Embed, Color, Member
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, lang
from lib.db import db


class Inventory(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='inventory', aliases=["inv"])
    @cooldown(1, 5, BucketType.user)
    async def inventory(self, ctx, member: Member = None):
        """Check someone's inventory to see what they have."""
        member = member or ctx.author

        inv = db.record("SELECT Inventory FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, member.id)
        rod, lock, gun, bomb = general.get_quantity(inv)
        inv_list = [[lang.get_message(ctx.language, 'INV_FishingRod'), rod, ":fishing_pole_and_fish:"],
                    [lang.get_message(ctx.language, 'INV_Lock'), lock, ":lock:"],
                    [lang.get_message(ctx.language, 'INV_Gun'), gun, ":gun:"]]

        desc = ""
        for i in inv_list:
            emote = ":white_check_mark:" if i[1] == 1 else ":x:"
            desc += f"{i[2]} {i[0]}: {emote}\n"
        desc += f":bomb: {lang.get_message(ctx.language, 'INV_Bomb')}: {bomb}x"

        embed = Embed(
            description=desc,
            color=Color.blue()
        )
        embed.set_author(name=lang.get_message(ctx.language, 'INV_InventoryOf') % member, icon_url=f"{member.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Inventory")


def setup(bot):
    bot.add_cog(Inventory(bot))
