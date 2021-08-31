from discord import Embed, Color
from discord.ext.commands import Cog, BucketType, cooldown, group

from lib.checks import general, jobs
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
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid Arguments. If you need help, use the `help` command.")

    @job.command(name='apply')
    async def apply(self, ctx, job_name):
        job_id = jobs.get_current_job_id(ctx.guild.id, ctx.author.id)
        experience = db.record("SELECT Experience FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
        current_job = jobs.get_job(job_id)
        all_jobs = jobs.get_all_jobs()
        job_name = job_name.lower()
        user_lvl = general.get_lvl(experience)

        for job in all_jobs:
            if job[1].lower() == job_name:
                if current_job[1].lower() == job_name:
                    await ctx.send("You already have this job.")
                    break
                elif int(job[3]) > user_lvl:
                    await ctx.send("You need to be atleast level %s to apply for this job. (You are now level %s.)" % (job[3], user_lvl))
                    break
                else:
                    db.execute("UPDATE userData SET CurrentJob = %s WHERE GuildID = %s AND UserID = %s", job[0], ctx.guild.id, ctx.author.id)
                    await ctx.send("You successfully applied for this job.")
                    break
        else:
            await ctx.send("This job does not exist. Please use `job info` to view all jobs.")

    @job.command(name='quit', aliases=['leave'])
    async def quit(self, ctx):
        if jobs.get_current_job_id(ctx.guild.id, ctx.author.id) == 1:
            await ctx.send("You don't have a job to quit.")
        else:
            db.execute("UPDATE userData SET CurrentJob = %s WHERE GuildID = %s AND UserID = %s", 1, ctx.guild.id, ctx.author.id)
            await ctx.send("You successfully quit your job.")

    @job.command(name='info', aliases=['information'])
    async def info(self, ctx):
        job_id = jobs.get_current_job_id(ctx.guild.id, ctx.author.id)
        experience = db.record("SELECT Experience FROM userData WHERE GuildID = %s AND UserID = %s", ctx.guild.id, ctx.author.id)
        current_job = jobs.get_job(job_id)
        all_jobs = jobs.get_all_jobs()

        extra = f"You are currently working as a **{current_job[1].title()}**.\n\n" if job_id != 1 else ""

        desc = ""
        user_lvl = general.get_lvl(experience)
        for job in all_jobs:
            desc += f"{'<:check:880822186930212864>' if user_lvl >= job[3] else '<:cross:880822172623470705>'} {job[1].title()} | Income: {job[4]} | Level: {job[3]}\n"

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
