from asyncio import TimeoutError
from io import BytesIO
from random import choice, shuffle, randint
from time import sleep

from PIL import Image, ImageFont, ImageDraw
from discord import Embed, Color, File
from discord.ext.commands import command, Cog, BucketType, cooldown
from essential_generators import DocumentGenerator

from lib.checks import general, lang, jobs
from lib.db import db

COMMAND = "work"
tasks = ["guess_the_word", "type_the_word", "math_calc", "multiple_choice", "remember"]
gen = DocumentGenerator()

questions = [
    ("What is the name for the Jewish New Year?", "d", ["Hanukkah", "Yom Kippur", "Kwanza", "Rosh Hashanah"])
]


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

    async def type_the_word(self, ctx):
        word = choice(self.words)
        timeout = len(word)

        font = ImageFont.truetype("data/fonts/OpenSans-Regular.ttf", 60)
        img = Image.new(mode="RGB", size=(500, 80), color=(54, 57, 63))

        draw = ImageDraw.Draw(img)
        draw.text((0, 0), word.upper(), (255, 255, 255), font=font)

        buffer = BytesIO()
        img.save(buffer, "png")
        buffer.seek(0)

        msg = await ctx.send(file=File(fp=buffer, filename="word.png"), embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_TypeTheWord') % timeout))

        if await self.wait_for_message(ctx, word, timeout):
            return msg
        else:
            await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_TypeTheWordFail'), Color.red()))
            return None

    async def math_calc(self, ctx):
        timeout = 15
        calculation = f"{randint(1, 50)} {choice(['+', '-', '*'])} {randint(1, 50)}"

        msg = await ctx.send(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_MathCalc') % (timeout, calculation)))

        if await self.wait_for_message(ctx, str(eval(calculation)), timeout):
            return msg
        else:
            await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_MathCalcFail') % eval(calculation), Color.red()))
            return None

    async def multiple_choice(self, ctx):
        timeout = 15
        question = choice(questions)

        answers = ['a', 'b', 'c', 'd']

        question_txt = f"{question[0]}\n\n"

        index = 0
        for answer in question[2]:
            question_txt += f"({answers[index]}) {answer}\n"
            index += 1

        msg = await ctx.send(embed=self.create_embed(ctx, question_txt))

        def check(message):
            return message.author == ctx.author and message.content.lower() in answers

        try:
            m = await self.bot.wait_for("message", timeout=timeout, check=check)

            if m.content.lower() == question[1]:
                return msg
        except TimeoutError:
            pass

        await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_MultipleChoiceFail') % question[1], Color.red()))
        return None

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
        /Requirements/ A job. Use `help job` for more info.
        """
        if general.check_status(ctx.guild.id, COMMAND):
            msg = await getattr(Work, choice(tasks))(self, ctx)
            if msg is not None:
                currency = general.get_currency(ctx.guild.id)
                current_job = db.record("SELECT CurrentJob FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
                all_jobs = jobs.get_jobs(ctx.guild.id)

                for job in all_jobs:
                    if job[2].lower() == current_job[0].lower():
                        income = job[4]
                        break
                else:
                    income = 0

                await msg.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'WORK_Success') % (currency, income), Color.green()))
                db.execute("UPDATE userData SET cash = cash + %s, netto = netto + %s WHERE GuildID = %s AND UserID = %s", income, income, ctx.guild.id, ctx.author.id)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Work(bot))
