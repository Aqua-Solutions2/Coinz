from asyncio import TimeoutError
from random import randint

import names
from discord import Embed, Color, Forbidden
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general

COMMAND = "beg"
emote_list = ['1️⃣', '2️⃣', '3️⃣']


class Beg(Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_random_payout():
        return randint(50, 800)

    @command()
    @cooldown(1, 600, BucketType.user)
    async def beg(self, ctx):
        """
        Ask for money from strangers. Some strangers won't give you money.
        /Payout/ Min: %CURRENCY%500\nMax: %CURRENCY%800
        """
        options = [names.get_first_name() for i in range(0, len(emote_list))]
        name_list = ""

        for i in range(0, len(emote_list)):
            name_list += f"{i + 1}. {options[i]}\n"

        embed = Embed(
            title=f"{COMMAND.title()}",
            description=f"You are going to beg for money. Choose the person you are going to ask for money:\n\n{name_list}",
            color=Color.blue()
        )
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        message = await ctx.send(embed=embed)

        try:
            for emote in emote_list:
                await message.add_reaction(emote)
        except Forbidden:
            await ctx.send("I don't have enough permissions to add emotes under messages. This command will not work if I don't have that permission.")
            return

        def check(reactie, gebruiker):
            return gebruiker == ctx.author and str(reactie.emoji) in emote_list

        try:
            reaction, member = await self.bot.wait_for("reaction_add", timeout=45, check=check)

            fail_index = randint(0, len(emote_list) - 1)
            user_index = emote_list.index(reaction.emoji)

            if fail_index == user_index:
                embed = Embed(
                    title=f"{COMMAND.title()}",
                    description="You chose %s, but this person gave you no money." % options[user_index],
                    color=Color.red()
                )
            else:
                payout = self.get_random_payout()

                new_amount = general.check_balance(ctx.guild.id, ctx.author.id, payout)
                if new_amount == 0:
                    await ctx.send("You have reached the maximum balance. You cannot make more money.")
                    return
                else:
                    payout = new_amount

                general.add_money(ctx.guild.id, ctx.author.id, payout)
                embed = Embed(
                    title=f"{COMMAND.title()}",
                    description="You chose %s, this person gave you %s%s." % (options[user_index], general.get_currency(ctx.guild.id), payout),
                    color=Color.green()
                )
        except TimeoutError:
            embed = Embed(
                title=f"{COMMAND.title()}",
                description="Unfortunately, because you waited too long everyone has walked by.",
                color=Color.red()
            )
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)

        try:
            await message.clear_reactions()
        except Exception:
            pass

        await message.edit(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Beg(bot))
