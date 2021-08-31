from math import ceil

from discord import Embed, Color, Member
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.db import db


class Inventory(Cog):
    ROWS_PER_PAGE = 5

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_inventory(guild_id, member_id, offset=0):
        return db.records(f"SELECT * FROM userInventory WHERE GuildID = %s AND UserID = %s ORDER BY ItemID DESC LIMIT 10 OFFSET {offset}", guild_id, member_id)

    @staticmethod
    def get_item(item_id):
        return db.record("SELECT * FROM globalInventory WHERE ItemID = %s", item_id)

    def create_inventory(self, inventory):
        description = ""
        if inventory:
            for row in inventory:
                item = self.get_item(row[3])
                description += f":{item[3]}: **{item[2].title()}** — {row[4]}\n__ID__ `{item[0]}` — {item[1].title()}\n\n"
        else:
            description = "No Items Found."
        return description

    def create_embed(self, member, guild_id, inventory, page):
        entire_inv = db.records(f"SELECT * FROM userInventory WHERE GuildID = %s AND UserID = %s", guild_id, member.id)
        embed = Embed(title="Owned Items", description=self.create_inventory(inventory), color=Color.blue())
        embed.set_author(name=f"Inventory of {member.display_name}", icon_url=f"{member.avatar_url}")
        embed.set_footer(text=f"{self.bot.FOOTER} | Page {page} of {ceil(len(entire_inv) / self.ROWS_PER_PAGE)}")
        return embed

    def calculate_offset(self, page):
        return (page - 1) * self.ROWS_PER_PAGE

    @command(name='inventory', aliases=["inv"])
    @cooldown(1, 5, BucketType.user)
    async def inventory(self, ctx, member: Member = None, page: int = 1):
        """Check someone's inventory to see what they have."""
        member = member or ctx.author
        offset = self.calculate_offset(page)
        inventory = self.get_inventory(ctx.guild.id, member.id, offset)
        await ctx.send(embed=self.create_embed(member, ctx.guild.id, inventory, page))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Inventory")


def setup(bot):
    bot.add_cog(Inventory(bot))
