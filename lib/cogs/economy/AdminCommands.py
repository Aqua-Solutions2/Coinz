from discord import Member
from discord.ext.commands import Cog, BucketType, cooldown, group, has_permissions

from lib.checks import general
from lib.db import db


class AdminCommands(Cog):
    MIN_BEDRAG = -1000000
    MAX_BEDRAG = 1000000000000

    def __init__(self, bot):
        self.bot = bot

    async def check_amount(self, ctx, member_id, amount):
        if not general.check_money(amount):
            await ctx.send("You have to give a valid number between %s and %s." % (self.MIN_BEDRAG, self.MAX_BEDRAG))
            return None

        new_amount = general.check_balance(ctx.guild.id, member_id, amount)

        if new_amount == 0:
            await ctx.send("This user has reached the maximum balance. You cannot give this user more money.")
            return None
        else:
            return new_amount

    @group(name="economy", aliases=["eco"])
    @cooldown(1, 5, BucketType.user)
    @has_permissions(administrator=True)
    async def economy(self, ctx):
        """
        Use Take | Give | Set or Reset to alter someone's balance.
        /Required Permissions/ Administrator
        /Subcommands/ `give <member> <amount> [cash | bank]` - Give a mamber some money.\n`take <member> <amount> [cash | bank]` - Take money from a member.\n`set <member> <amount> [cash | bank]` - Set the money of a member.\n`reset <member>` - Reset someone's balance..
        /Examples/ `economy give Siebe 9999 cash`\n`economy take @Siebe 9999`\n`economy set Siebe#9999 9999 bank`\n`economy reset Siebe`
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid Arguments. If you need help, use the `help` command.")

    @economy.command(aliases=["add"])
    async def give(self, ctx, member: Member, amount: int, location: str = "cash"):
        general.create_row(ctx.guild.id, member.id)
        amount = await self.check_amount(ctx, member.id, amount)

        if amount is None:
            return

        if location.lower() in ["cash", "bank"]:
            currency = general.get_currency(ctx.guild.id)
            db.execute(f"UPDATE userData SET {location.lower()} = {location.lower()} + %s, Net = Net + %s WHERE GuildID = %s AND UserID = %s", amount, amount, ctx.guild.id, member.id)
            await ctx.send("Succesfully given %s%s to %s." % (currency, amount, member))
        else:
            await ctx.send("Invalid Type. Valid types are: %s." % "Cash, Bank")

    @economy.command(aliases=["remove"])
    async def take(self, ctx, member: Member, amount: int, location: str = "cash"):
        general.create_row(ctx.guild.id, member.id)
        amount = await self.check_amount(ctx, member.id, amount)

        if amount is None:
            return

        if location.lower() in ["cash", "bank"]:
            currency = general.get_currency(ctx.guild.id)
            db.execute(f"UPDATE userData SET {location.lower()} = {location.lower()} - %s, Net = Net - %s WHERE GuildID = %s AND UserID = %s", amount, amount, ctx.guild.id, member.id)
            await ctx.send("Succesfully taken %s%s from %s." % (currency, amount, member))
        else:
            await ctx.send("Invalid Type. Valid types are: %s." % "Cash, Bank")

    @economy.command(name="set")
    async def set_(self, ctx, member: Member, amount: int, location: str = "cash"):
        general.create_row(ctx.guild.id, member.id)
        amount = await self.check_amount(ctx, member.id, amount)

        if amount is None:
            return

        if location.lower() in ["cash", "bank"]:
            currency = general.get_currency(ctx.guild.id)
            db.execute(f"UPDATE userData SET {location.lower()} = %s WHERE GuildID = %s AND UserID = %s", amount, ctx.guild.id, member.id)
            db.execute("UPDATE userData SET Net = cash + bank WHERE GuildID = %s AND UserID = %s", ctx.guild.id, member.id)
            await ctx.send("Succesfully set balance from %s to %s%s" % (member, currency, amount))
        else:
            await ctx.send("Invalid Type. Valid types are: %s." % "Cash, Bank")

    @economy.command(name="reset")
    async def reset_(self, ctx, member: Member):
        db.execute("DELETE FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, member.id)
        await ctx.send("Balance of %s has been reset." % member)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("AdminCommands")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
