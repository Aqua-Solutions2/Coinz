from discord import Embed, Color, Member
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, lang
from lib.db import db


class Money(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def print_account_balance(self, ctx, member, currency, cash, bank, netto):
        embed = Embed(color=Color.blue())
        embed.add_field(name=lang.get_message(ctx.language, 'MONEY_Cash'), value=f"{currency}{cash}", inline=True)
        embed.add_field(name=lang.get_message(ctx.language, 'MONEY_Bank'), value=f"{currency}{bank}", inline=True)
        embed.add_field(name=lang.get_message(ctx.language, 'MONEY_Total'), value=f"{currency}{netto}", inline=True)
        embed.set_author(name=lang.get_message(ctx.language, 'MONEY_AccountOf') % member, icon_url=f"{member.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        await ctx.send(embed=embed)

    @staticmethod
    async def calculate_money(ctx, money, max_money):
        money_calculated = -1

        if money == "all":
            money_calculated = max_money
        else:
            try:
                money = int(money)
                if max_money <= 0:
                    await ctx.send(lang.get_message(ctx.language, 'MONEY_NoBalance'))
                elif 0 < money <= max_money:
                    money_calculated = money
                else:
                    await ctx.send(lang.get_message(ctx.language, 'CMD_NumberExceedLimit') % (1, max_money))
            except ValueError:
                await ctx.send(lang.get_message(ctx.language, 'ERR_InvalidArguments'))

        return money_calculated

    @command(name="account", aliases=["balance", "bal"])
    @cooldown(1, 5, BucketType.user)
    async def account(self, ctx, member: Member = None):
        """View your account balance and see how much cash|bank|total you have."""
        member = member or ctx.author
        userdata = db.record("SELECT * FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, member.id)
        await self.print_account_balance(ctx, member, general.get_currency(ctx.guild.id), userdata[3], userdata[4], userdata[3]+userdata[4])

    @command(name="deposit", aliases=["dep"])
    @cooldown(1, 5, BucketType.user)
    async def deposit(self, ctx, amount):
        """
        Deposit cash into your bank account.
        /Extra/ Amount can be a number or `all`. All means that you want to select all money you have.
        """
        cash = db.record("SELECT cash FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)

        money = await self.calculate_money(ctx, amount, cash[0])
        if money == -1:
            return

        db.execute("UPDATE userData SET cash = cash - %s, bank = bank + %s WHERE GuildID = %s AND UserID = %s", money, money, ctx.guild.id, ctx.author.id)
        await ctx.send(":white_check_mark: " + lang.get_message(ctx.language, 'MONEY_Deposit') % (general.get_currency(ctx.guild.id), money))

    @command(name="withdraw", aliases=["with"])
    @cooldown(1, 5, BucketType.user)
    async def withdraw(self, ctx, amount):
        """
        Withdraw cash from your bank account.
        /Extra/ Amount can be a number or `all`. All means that you want to select all money you have.
        """
        bank = db.record("SELECT bank FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)

        money = await self.calculate_money(ctx, amount, bank[0])
        if money == -1:
            return

        db.execute("UPDATE userData SET cash = cash + %s, bank = bank - %s WHERE GuildID = %s AND UserID = %s", money, money, ctx.guild.id, ctx.author.id)
        await ctx.send(":white_check_mark: " + lang.get_message(ctx.language, 'MONEY_Withdraw') % (general.get_currency(ctx.guild.id), money))

    @command(name="pay", aliases=["give-money"])
    @cooldown(1, 5, BucketType.user)
    async def pay(self, ctx, member: Member, amount):
        """
        Pay someone some cash.
        /Extra/ Amount can be a number or `all`. All means that you want to select all money you have.
        """
        if general.check_status(ctx.guild.id, "pay"):
            cash_author = db.record("SELECT cash FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)

            money = await self.calculate_money(ctx, amount, cash_author[0])
            if money == -1:
                return

            general.create_row(ctx.guild.id, member.id)
            new_money = general.check_balance(ctx.guild.id, member.id, money)
            if new_money == 0:
                await ctx.send(lang.get_message(ctx.language, 'CMD_ExceedBalLimitMember'))
                return
            else:
                money = new_money

            db.execute("UPDATE userData SET cash = cash - %s, netto = netto - %s WHERE GuildID = %s AND UserID = %s", money, money, ctx.guild.id, ctx.author.id)
            db.execute("UPDATE userData SET cash = cash + %s, netto = netto + %s WHERE GuildID = %s AND UserID = %s", money, money, ctx.guild.id, member.id)
            await ctx.send(lang.get_message(ctx.language, 'MONEY_Pay') % (member, general.get_currency(ctx.guild.id), money))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Money")


def setup(bot):
    bot.add_cog(Money(bot))
