from discord import Embed, Color, Member
from discord.ext.commands import Cog, command, cooldown, BucketType

from lib.checks import general
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

    @command(name="profile", aliases=["userinfo", "user-info", "memberinfo", "member-info"])
    @cooldown(1, 10, BucketType.user)
    async def profile(self, ctx, member: Member = None):
        """Get a lot of information about a member."""
        member = member or ctx.author
        general.create_row(ctx.guild.id, member.id)
        user_data = db.record("SELECT * FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, member.id)

        fields = [
            {"name": "Cash", "value": f"{user_data[3]}"},
            {"name": "Bank", "value": f"{user_data[4]}"},
            {"name": "Net", "value": f"{user_data[5]}"},
            {"name": "Experience", "value": f"{user_data[7]}"},
            {"name": "Level", "value": f"{int(user_data[7] / 100)}"},
            {"name": "Job", "value": f"{user_data[6].title()}"},
            {"name": "Followers", "value": f"{user_data[9]}"},
            {"name": "Likes", "value": f"{user_data[8]}"}
        ]
        await ctx.send(embed=self.create_embed(fields, member, f"User Info of {member.display_name}", member.color))

    @command(name="guild-info", aliases=["guildinfo", "server-info", "serverinfo"])
    @cooldown(1, 10, BucketType.guild)
    async def guild_info(self, ctx):
        """Get general information about this server."""
        guild_data = db.record("SELECT * FROM guilds WHERE GuildID = %s", ctx.guild.id)
        total = db.column("SELECT Net FROM userData WHERE GuildID = %s", ctx.guild.id)

        fields = [
            {"name": "Prefix", "value": f"{guild_data[1]}"},
            {"name": "Currency", "value": f"{guild_data[2]}"},
            {"name": "Premium Status", "value": f"{'Active' if int(guild_data[3]) == 1 else 'FREE TIER'}"},
            {"name": "Total Money", "value": f"{guild_data[2]}{sum(total)}"}
        ]
        await ctx.send(embed=self.create_embed(fields, ctx.author, "Guild Info"))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Info")


def setup(bot):
    bot.add_cog(InfoCmds(bot))
