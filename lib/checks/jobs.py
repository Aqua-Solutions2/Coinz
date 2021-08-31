from lib.db import db


def get_current_job_id(guild_id, member_id):
    return db.record("SELECT CurrentJob FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, member_id)[0]


def get_job(job_id):
    return db.record("SELECT * FROM globalJobs WHERE JobID = %s", job_id)


def get_all_jobs():
    return db.records("SELECT * FROM globalJobs ORDER BY UnlockLvl")


if __name__ == '__main__':
    print("This file is not meant to be running seperatly from the bot.py file.")
