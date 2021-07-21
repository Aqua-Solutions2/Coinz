from discord import Member, Embed, Color
from discord.ext.commands import Cog, command, cooldown, BucketType, CooldownMapping
from random import randint
from lib.db import db
from typing import Optional
from math import ceil
from asyncio import TimeoutError


class Experience(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cd_mapping = CooldownMapping.from_cooldown(1, 60, BucketType.member)

    @staticmethod
    def add_xp(xp, guild_id, member_id):
        db.execute("UPDATE userData SET Experience = Experience + %s, Messages = Messages + 1 WHERE GuildID = %s AND UserID = %s", xp, guild_id, member_id)

    @staticmethod
    def check_lvl(xp):
        return int((xp // 42) ** 0.55)

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
                member = "Onbekend#0000"

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
            title=f"Levels Scoreboard van {guild}",
            description=f"```md\n{header}\n{'=' * langste_row}\n{rows}```",
            color=Color.blue()
        )
        embed.set_footer(text=f"{self.bot.FOOTER} | Pagina {current_page}/{max_pages}")
        return embed

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            user = db.record("SELECT UserID FROM userData WHERE GuildID = %s AND UserID = %s", message.guild.id, message.author.id)

            if user is None:
                db.execute("INSERT IGNORE userData (GuildID, UserID) VALUES (%s, %s)", message.guild.id, message.author.id)

            self.add_xp(randint(7, 15), message.guild.id, message.author.id)

            new_xp, old_lvl = db.record("SELECT Experience, XpLevel FROM userData WHERE GuildID = %s AND UserID = %s", message.guild.id, message.author.id)
            new_lvl = self.check_lvl(new_xp)

            if new_lvl > old_lvl:
                db.execute("UPDATE userData SET XpLevel = %s WHERE GuildID = %s AND UserID = %s", new_lvl, message.guild.id, message.author.id)

    @command()
    @cooldown(1, 5, BucketType.user)
    async def rank(self, ctx, member: Optional[Member]):
        member = member or ctx.author

        user = db.record("SELECT UserID FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
        if user is None:
            await ctx.send(":x: Deze gebruiker heeft nog geen gebruikers data.")
        else:
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
        records_per_page = 20
        offset = (page - 1) * records_per_page

        header = "Num. | Experience | LvL | Member"
        header_columns = header.replace(' ', '').split('|')

        rows, langste_row = self.generate_rows(ctx.guild.id, records_per_page, offset, header_columns)

        if rows == "":
            rows = "Geen gegevens gevonden."

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
            await message.clear_reaction("◀️")
            await message.clear_reaction("▶️")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Experience")


def setup(bot):
    bot.add_cog(Experience(bot))
