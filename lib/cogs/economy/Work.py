from asyncio import TimeoutError
from random import choice, shuffle, randint
from time import sleep

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown
from essential_generators import DocumentGenerator

from lib.checks import general, lang
from lib.db import db

COMMAND = "work"

# Final List: ["guess_the_word", "type_the_word", "math_calc", "multiple_choice", "remember"]
jobs = ["guess_the_word", "math_calc", "remember"]

gen = DocumentGenerator()


class Work(Cog):
    def __init__(self, bot):
        self.bot = bot

        file = open(f'data/extra/word_list.txt', 'r')
        words = file.readlines()
        file.close()
        self.words = [x.replace('\n', '') for x in words]

    def create_embed(self, ctx, desc, color=Color.blue()):
        embed = Embed(description=desc, color=color)
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    async def wait_for_message(self, ctx, content, timeout):
        def check(message):
            return message.author == ctx.author and message.content.lower() == content.lower()

        try:
            await self.bot.wait_for("message", timeout=timeout, check=check)
            return True
        except TimeoutError:
            return False

    async def guess_the_word(self, ctx):
        timeout = 30
        word = choice(self.words)

        word_list = list(word.lower())
        shuffle(word_list)
        obfuscated_word = "".join(word_list)
        msg = await ctx.send(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_GuessTheWord') % (timeout, obfuscated_word)))

        if await self.wait_for_message(ctx, word, timeout):
            return msg
        else:
            await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_GuessTheWordFail') % word, Color.red()))
            return None

    # async def type_the_word(self, ctx):
    #     pass

    async def math_calc(self, ctx):
        timeout = 15
        calculation = f"{randint(1, 50)} {choice(['+', '-', '*'])} {randint(1, 50)}"

        msg = await ctx.send(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_MathCalc') % (timeout, calculation)))

        if await self.wait_for_message(ctx, str(eval(calculation)), timeout):
            return msg
        else:
            await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_MathCalcFail') % eval(calculation), Color.red()))
            return None

    # async def multiple_choice(self, ctx):
    #     pass

    async def remember(self, ctx):
        sentence = gen.sentence()
        sleep_time = len(sentence.split(' ')) * 0.5
        timeout = 30
        msg = await ctx.send(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_Remember') % sentence))
        sleep(sleep_time)
        await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_RememberSentence')))

        if await self.wait_for_message(ctx, sentence, timeout):
            return msg
        else:
            await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_RememberFail'), Color.red()))
            return None

    @command(name="work")
    @cooldown(1, 3600, BucketType.user)
    async def work(self, ctx):
        """
        Work as a normal person to get rich.
        /Payout/ %JOBS%
        /Requirements/ A job.
        """
        if general.check_status(ctx.guild.id, COMMAND):
            payout = general.get_payout(ctx.guild.id, COMMAND)
            currency = general.get_currency(ctx.guild.id)
            msg = await getattr(Work, choice(jobs))(self, ctx)

            if msg is not None:
                await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_Success') % (currency, payout), Color.green()))
                db.execute("UPDATE userData SET cash = cash + %s, netto = netto + %s WHERE GuildID = %s AND UserID = %s", payout, payout, ctx.guild.id, ctx.author.id)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Work(bot))
