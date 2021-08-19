from random import randint

from discord import Embed, Color, Member
from discord.ext.commands import Cog, BucketType, cooldown, group

from lib.checks import general, lang
from lib.db import db

COMMAND = "social"


class Social(Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_followers(guild_id, user_id):
        followers = db.record("SELECT SocialFollowers FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)
        return followers[0]

    @staticmethod
    def get_likes(guild_id, user_id):
        likes = db.record("SELECT SocialLikes FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)
        return likes[0]

    @group(name='social', aliases=["social-media"])
    @cooldown(1, 5, BucketType.user)
    async def social(self, ctx):
        """
        Manage your social media account.
        /Subcommands/ `post` - Post something on your account.\n`view [member]` - View the likes and followers of someone.\n`register` - Create a social media account.\n`delete` - Delete your account.
        /Examples/ `social view Siebe`\n`social post`\n`social register`\n`social delete`
        /Beta/ This command has no real purpose as of now. When the bot will be released you can get money from your likes and sell your account.
        """
        if general.check_status(ctx.guild.id, COMMAND):
            if ctx.invoked_subcommand is None:
                await ctx.send(lang.get_message(ctx.language, 'ERR_InvalidArguments'))
        else:
            return

    @social.command(name="post")
    @cooldown(1, 7200, BucketType.user)
    async def post(self, ctx):
        followers = self.get_followers(ctx.guild.id, ctx.author.id)
        if followers == 0:
            await ctx.send(lang.get_message(ctx.language, 'SOCIAL_NoAccount'))
            ctx.command.reset_cooldown(ctx)
        else:
            new_followers = randint(1, 30) if followers < 200 else randint(0, 0.2 * followers)
            new_likes = randint(1, 5) if followers < 200 else randint(0, 0.05 * followers)
            db.execute("UPDATE userData SET SocialFollowers = SocialFollowers + %s, SocialLikes = SocialLikes + %s WHERE GuildID = %s AND UserID = %s", new_followers, new_likes, ctx.guild.id, ctx.author.id)
            await ctx.send(lang.get_message(ctx.language, 'SOCIAL_Post') % (new_followers, new_likes))

    @social.command(name="view")
    async def view(self, ctx, member: Member = None):
        member = member or ctx.author
        embed = Embed(color=Color.blue())
        embed.add_field(name=lang.get_message(ctx.language, 'SOCIAL_Followers'), value=f"{self.get_followers(ctx.guild.id, member.id)} :busts_in_silhouette:", inline=True)
        embed.add_field(name=lang.get_message(ctx.language, 'SOCIAL_Likes'), value=f"{self.get_likes(ctx.guild.id, member.id)} :heart:", inline=True)
        embed.set_author(name=f"{COMMAND.title()} {lang.get_message(ctx.language, 'MONEY_AccountOf').lower() % member}", icon_url=f"{member.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        await ctx.send(embed=embed)

    @social.command(name="register", aliases=['create'])
    async def register_(self, ctx):
        if self.get_followers(ctx.guild.id, ctx.author.id) == 0:
            db.execute("UPDATE userData SET SocialFollowers = 1 WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
            await ctx.send(lang.get_message(ctx.language, 'SOCIAL_CreateAccount'))
        else:
            await ctx.send(lang.get_message(ctx.language, 'SOCIAL_AccountAlreadyexists'))

    @social.command(name="delete")
    async def delete_(self, ctx):
        if self.get_followers(ctx.guild.id, ctx.author.id) == 0:
            await ctx.send(lang.get_message(ctx.language, 'SOCIAL_NoAccount'))
        else:
            db.execute("UPDATE userData SET SocialFollowers = 0, SocialLikes = 0 WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
            await ctx.send(lang.get_message(ctx.language, 'SOCIAL_DeleteAccount'))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Social(bot))
