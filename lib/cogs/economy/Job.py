from discord import Embed, Color
from discord.ext.commands import Cog, BucketType, cooldown, group

from lib.checks import general, lang, jobs
from lib.db import db


class Job(Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(name='job', aliases=["jobs"])
    @cooldown(1, 5, BucketType.user)
    async def job(self, ctx):
        """
        Apply or Quit your current job. You can also view all jobs here.
        /Subcommands/ `apply <job>` - Apply for a job.\n`quit` - Quit your current job.\n`info` - View all available jobs and your current job.
        /Examples/ `job apply cashier`\n`job quit`\n`job info`
        """
        if general.check_status(ctx.guild.id, "work"):
            if ctx.invoked_subcommand is None:
                await ctx.send(lang.get_message(ctx.language, 'ERR_InvalidArguments'))
        else:
            return

    @job.command(name='apply')
    async def apply(self, ctx, job_name):
        user_data = db.record("SELECT * FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
        all_jobs = jobs.get_jobs(ctx.guild.id)
        current_job = jobs.get_job(user_data[6], all_jobs)
        job_name = job_name.lower()

        for job in all_jobs:
            if job[2].lower() == job_name:
                if current_job[2].lower() == job_name:
                    await ctx.send(lang.get_message(ctx.language, 'JOB_AlreadyHasJob'))
                    break
                elif int(job[3]) > int(user_data[10]):
                    await ctx.send(lang.get_message(ctx.language, 'JOB_LvlToHigh') % (job[3], user_data[10]))
                    break
                else:
                    db.execute("UPDATE userData SET CurrentJob = %s WHERE GuildID = %s AND UserID = %s", job_name, ctx.guild.id, ctx.author.id)
                    await ctx.send(lang.get_message(ctx.language, 'JOB_Applied'))
                    break
        else:
            await ctx.send(lang.get_message(ctx.language, 'JOB_NotFound'))

    @job.command(name='quit', aliases=['leave'])
    async def quit(self, ctx):
        user_data = db.record("SELECT * FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)

        if user_data[6] == "unemployed":
            await ctx.send(lang.get_message(ctx.language, 'JOB_NoJob'))
        else:
            db.execute("UPDATE userData SET CurrentJob = %s WHERE GuildID = %s AND UserID = %s", "unemployed", ctx.guild.id, ctx.author.id)
            await ctx.send(lang.get_message(ctx.language, 'JOB_Quit'))

    @job.command(name='info', aliases=['information'])
    async def info(self, ctx):
        current_job = db.record("SELECT CurrentJob FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
        all_jobs = jobs.get_jobs(ctx.guild.id)

        desc = ""
        index = 1

        income_txt = lang.get_message(ctx.language, 'JOB_Income')
        unlocked_at_txt = lang.get_message(ctx.language, 'JOB_UnlockedAt')
        extra = f"{lang.get_message(ctx.language, 'JOB_UserJob') % current_job[0]}\n\n" if current_job[0] != "unemployed" else ""

        for job in all_jobs:
            desc += f"**{index}.** {job[2].title()} | {income_txt}: {job[4]} | {unlocked_at_txt}: {job[3]}\n"
            index += 1

        embed = Embed(
            description=f"{extra}{desc}",
            color=Color.blue()
        )
        embed.set_author(name="Job Leaderboard", icon_url=f"{self.bot.user.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Job")


def setup(bot):
    bot.add_cog(Job(bot))
