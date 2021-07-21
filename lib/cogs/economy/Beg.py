from discord import Embed, Color, Forbidden
from discord.ext.commands import command, Cog, BucketType, cooldown
from lib.checks import general, lang
from random import randint
import names
from asyncio import TimeoutError

COMMAND = "beg"
emote_list = ['1️⃣', '2️⃣', '3️⃣']


class Beg(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    @cooldown(1, 600, BucketType.user)
    async def beg(self, ctx):
        if general.check_status(ctx.guild.id, COMMAND):
            options = [names.get_first_name() for i in range(0, len(emote_list))]
            name_list = ""

            for i in range(0, len(emote_list)):
                name_list += f"{i+1}. {options[i]}\n"

            embed = Embed(
                title=f"{COMMAND.title()}",
                description=f"{lang.get_message(ctx.language, 'BEDEL_General')}\n\n{name_list}",
                color=Color.blue()
            )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text=self.bot.FOOTER)
            message = await ctx.send(embed=embed)

            try:
                for emote in emote_list:
                    await message.add_reaction(emote)
            except Forbidden:
                await ctx.send(lang.get_message(ctx.language, "CMD_ForbiddenEmotes"))
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
                        description=lang.get_message(ctx.language, "BEDEL_NoMoney") % options[user_index],
                        color=Color.red()
                    )
                else:
                    payout = general.get_payout(ctx.guild.id, COMMAND)

                    new_amount = general.check_balance(ctx.guild.id, ctx.author.id, payout)
                    if new_amount == 0:
                        await ctx.send(lang.get_message(ctx.language, 'CMD_ExceedBalLimitAuthor'))
                        return
                    else:
                        payout = new_amount

                    general.add_money(ctx.guild.id, ctx.author.id, payout)
                    embed = Embed(
                        title=f"{COMMAND.title()}",
                        description=lang.get_message(ctx.language, "BEDEL_GetMoney") % (options[user_index], general.get_currency(ctx.guild.id), payout),
                        color=Color.green()
                    )
            except TimeoutError:
                embed = Embed(
                    title=f"{COMMAND.title()}",
                    description=lang.get_message(ctx.language, "BEDEL_TimeoutError"),
                    color=Color.red()
                )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text=self.bot.FOOTER)

            try:
                await message.clear_reactions()
            except Exception:
                pass

            await message.edit(embed=embed)
        else:
            ctx.command.reset_cooldown(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Beg(bot))
