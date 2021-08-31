from asyncio import TimeoutError
from math import ceil
from typing import Optional

from discord import Member, Embed, Color
from discord.ext.commands import Cog, command, cooldown, BucketType, CooldownMapping

from lib.db import db


class Experience(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cd_mapping = CooldownMapping.from_cooldown(1, 60, BucketType.member)

    def generate_rows(self, guild_id, records_per_page, offset, header_columns):
        userdata = db.records(f"SELECT * FROM userData WHERE GuildID = %s ORDER BY Experience DESC LIMIT {records_per_page} OFFSET {offset}", guild_id)

        nummer = offset
        rows = ""
        langste_row = 0
        for user in userdata:
            nummer += 1

            xp = user[9]
            lvl = user[10]

            try:
                member = self.bot.get_user(user[2])
            except Exception:
                db.execute("DELETE FROM userData WHERE GuildID = %s and UserID = %s", guild_id, user[2])
                member = user[2]

            nr_spacing = " " * (len(header_columns[0]) - len(str(nummer)) - 1)
            xp_spacing = " " * (len(header_columns[1]) - len(str(xp)))
            lvl_spacing = " " * (len(header_columns[2]) - len(str(lvl)))

            row = f"{nummer}.{nr_spacing} | {xp}{xp_spacing} | {lvl}{lvl_spacing} | {member}\n"
            rows += row

            if len(row) > langste_row:
                langste_row = len(row)
        return rows, langste_row

    def create_embed(self, header, langste_row, rows, guild, current_page, max_pages):
        embed = Embed(
            title=f"Scoreboard of {guild}",
            description=f"```md\n{header}\n{'=' * langste_row}\n{rows}```",
            color=Color.blue()
        )
        embed.set_footer(text=f"{self.bot.FOOTER} | Pagina {current_page}/{max_pages}")
        return embed

    @command()
    @cooldown(1, 5, BucketType.user)
    async def rank(self, ctx, member: Optional[Member]):
        """Displays the current level a member is."""
        member = member or ctx.author
        xp, msg, lvl = db.record("SELECT Experience, Messages, XpLevel FROM userData WHERE GuildId = %s AND UserID = %s", ctx.guild.id, member.id)

        embed = Embed(
            title=f"Rank van {member}",
            color=member.color
        )
        embed.add_field(name="Experience", value=f"{xp}", inline=True)
        embed.add_field(name="Level", value=f"{lvl}", inline=True)
        embed.add_field(name="Berichten", value=f"{msg}", inline=True)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=self.bot.FOOTER)
        await ctx.send(embed=embed)

    @command()
    @cooldown(1, 5, BucketType.user)
    async def levels(self, ctx, page: int = 1):
        """Displays a leaderboard with 20 users per page."""
        records_per_page = 20
        offset = (page - 1) * records_per_page

        header = "Num. | Experience | LvL | Member"
        header_columns = header.replace(' ', '').split('|')

        rows, langste_row = self.generate_rows(ctx.guild.id, records_per_page, offset, header_columns)

        if rows == "":
            rows = "No Records Found."

        current_page = offset // records_per_page + 1
        max_pages = ceil(len(db.records("SELECT * FROM userData WHERE GuildID = %s", ctx.guild.id)) / records_per_page)

        embed = self.create_embed(header, langste_row, rows, ctx.guild, current_page, max_pages)
        message = await ctx.send(embed=embed)

        if max_pages > 1:
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reactie, gebruiker):
                return gebruiker == ctx.author and str(reactie.emoji) in ["◀️", "▶️"]

            while True:
                try:
                    reaction, member = await self.bot.wait_for("reaction_add", timeout=30, check=check)
                    nieuwe_pagina = True

                    if str(reaction.emoji) == "▶️" and page != max_pages:
                        page += 1
                    elif str(reaction.emoji) == "◀️" and page > 1:
                        page -= 1
                    else:
                        nieuwe_pagina = False

                    await message.remove_reaction(reaction, member)

                    if nieuwe_pagina:
                        offset = (page - 1) * records_per_page
                        current_page = offset // records_per_page + 1

                        rows, langste_row = self.generate_rows(ctx.guild.id, records_per_page, offset, header_columns)
                        embed = self.create_embed(header, langste_row, rows, ctx.guild, current_page, max_pages)
                        await message.edit(embed=embed)
                except TimeoutError:
                    break
            await message.clear_reactions()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Experience")


def setup(bot):
    bot.add_cog(Experience(bot))
