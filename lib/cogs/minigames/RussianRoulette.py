from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown
from lib.checks import general, lang, minigames
from random import randint
from asyncio import TimeoutError, sleep

COMMAND = "RussianRoulette"
EMOTES = ["❌", "🔫"]


class RussianRoulette(Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, ctx, desc, currency, bet, multiplier, color=Color.blue()):
        embed = Embed(description=desc, color=color)
        embed.add_field(name=lang.get_message(ctx.language, 'CMD_Multiplier'), value=f"{multiplier}x", inline=True)
        embed.add_field(name=lang.get_message(ctx.language, 'CMD_Profit'), value=f"{currency}{int(bet * multiplier)}", inline=True)
        embed.set_author(name=COMMAND, icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @command(name="russian-roulette", aliases=["rroulette", "rr"])
    @cooldown(3, 3600, BucketType.user)
    async def russian_roulette(self, ctx, bet: int):
        if general.check_status(ctx.guild.id, COMMAND.lower()):
            err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet, COMMAND.lower())

            if err_msg is not None:
                await ctx.send(lang.get_message(ctx.language, err_msg))
                return

            general.remove_money(ctx.guild.id, ctx.author.id, bet)

            bullet = randint(1, 6)
            hole = 1
            multiplier = 1.0

            currency = general.get_currency(ctx.guild.id)
            message = await ctx.send(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'RUSROULETTE_Start'), currency, bet, multiplier))
            await sleep(2)
            await message.add_reaction(EMOTES[0])
            await message.add_reaction(EMOTES[1])

            def check(reactie, gebruiker):
                return gebruiker == ctx.author and str(reactie.emoji) in EMOTES

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=10)
                    emote = reaction.emoji

                    await message.remove_reaction(emoji=emote, member=ctx.author)

                    if emote == EMOTES[0]:
                        general.add_money(ctx.guild.id, ctx.author.id, int(bet * multiplier))
                        await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'RUSROULETTE_Quit'), currency, bet, multiplier, Color.green()))
                        await message.clear_reactions()
                        break
                    else:
                        hole += 1
                        multiplier = round(multiplier + 0.5, 1)
                        await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'RUSROULETTE_PullingTrigger'), currency, bet, multiplier))
                        await sleep(1.5)

                    if hole == bullet:
                        await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'RUSROULETTE_Killed'), currency, bet, multiplier, Color.red()))
                        await message.clear_reactions()
                        await message.add_reaction("☠️")
                        break
                    else:
                        await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'RUSROULETTE_Missed'), currency, bet, multiplier))
                except TimeoutError:
                    embed = Embed(description=lang.get_message(ctx.language, 'CMD_NoResponds'), color=Color.red())
                    embed.set_author(name=COMMAND, icon_url=f"{ctx.author.avatar_url}")
                    embed.set_footer(text=self.bot.FOOTER)
                    await message.edit(embed=embed)
                    break
        else:
            ctx.command.reset_cooldown(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND)


def setup(bot):
    bot.add_cog(RussianRoulette(bot))
