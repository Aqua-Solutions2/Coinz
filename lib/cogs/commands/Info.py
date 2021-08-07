from discord import Embed, Color, Member
from discord.ext.commands import Cog, command, cooldown, BucketType

from lib.checks import general, lang
from lib.db import db


class InfoCmds(Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, fields, member, cmd, color=Color.blue()):
        embed = Embed(color=color)
        for field in fields:
            embed.add_field(name=field['name'], value=field['value'], inline=True)
        embed.set_footer(text=self.bot.FOOTER)
        embed.set_author(name=f"{cmd}", icon_url=f"{member.avatar_url}")
        return embed

    @command(name="user-info", aliases=["userinfo", "memberinfo", "member-info"])
    @cooldown(1, 10, BucketType.user)
    async def user_info(self, ctx, member: Member = None):
        member = member or ctx.author
        general.create_row(ctx.guild.id, member.id)
        user_data = db.record("SELECT * FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, member.id)

        fields = [
            {"name": lang.get_message(ctx.language, 'MONEY_Cash'), "value": f"{user_data[3]}"},
            {"name": lang.get_message(ctx.language, 'MONEY_Bank'), "value": f"{user_data[4]}"},
            {"name": lang.get_message(ctx.language, 'MONEY_Total'), "value": f"{user_data[5]}"},
            {"name": lang.get_message(ctx.language, 'EXP_Experience'), "value": f"{user_data[9]}"},
            {"name": lang.get_message(ctx.language, 'EXP_Messages'), "value": f"{user_data[8]}"},
            {"name": lang.get_message(ctx.language, 'EXP_Level'), "value": f"{user_data[10]}"},
            {"name": lang.get_message(ctx.language, 'WORK_Job'), "value": f"{user_data[6].title()}"},
            {"name": lang.get_message(ctx.language, 'SOCIAL_Followers'), "value": f"{user_data[12]}"},
            {"name": lang.get_message(ctx.language, 'SOCIAL_Likes'), "value": f"{user_data[11]}"}
        ]
        await ctx.send(embed=self.create_embed(fields, member, f"User Info of {member.display_name}", member.color))

    @command(name="guild-info", aliases=["guildinfo", "server-info", "serverinfo"])
    @cooldown(1, 10, BucketType.guild)
    async def guild_info(self, ctx):
        guild_data = db.record("SELECT * FROM guilds WHERE GuildID = %s", ctx.guild.id)
        total = db.column("SELECT Netto FROM userData WHERE GuildID = %s", ctx.guild.id)

        fields = [
            {"name": lang.get_message(ctx.language, 'INFO_Prefix'), "value": f"{guild_data[1]}"},
            {"name": lang.get_message(ctx.language, 'INFO_Currency'), "value": f"{guild_data[2]}"},
            {"name": lang.get_message(ctx.language, 'INFO_Premium'), "value": f"{'Active' if int(guild_data[4]) == 1 else 'FREE TIER'}"},
            {"name": lang.get_message(ctx.language, 'INFO_Language'), "value": f"{guild_data[3]}"},
            {"name": f"{lang.get_message(ctx.language, 'MONEY_Total')} {lang.get_message(ctx.language, 'MONEY_Money')}", "value": f"{guild_data[2]}{sum(total)}"}
        ]
        await ctx.send(embed=self.create_embed(fields, ctx.author, "Guild Info"))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Info")


def setup(bot):
    bot.add_cog(InfoCmds(bot))
