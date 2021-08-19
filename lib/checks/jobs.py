from lib.db import db

DEFAULT = ((0, 0, "cashier", 0, 210),
           (0, 0, "janitor", 1, 250),
           (0, 0, "housekeeper", 2, 280),
           (0, 0, "teacher", 3, 340),
           (0, 0, "construction worker", 5, 390),
           (0, 0, "mechanic", 7, 460),
           (0, 0, "electrician", 8, 490),
           (0, 0, "police officer", 10, 550),
           (0, 0, "lawyer", 12, 680),
           (0, 0, "software Developer", 16, 720),
           (0, 0, "dentist", 20, 800))


def get_jobs(guild_id):
    all_jobs = db.records("SELECT * FROM guildWorkPayouts WHERE GuildID = %s ORDER BY Loon", guild_id)
    return DEFAULT if not all_jobs else all_jobs


def get_job(current_job, all_jobs):
    for job in all_jobs:
        if current_job == job[2]:
            job_tuple = job
            break
    else:
        job_tuple = (0, 0, "unemployed", 0, 0)
    return job_tuple


def set_job(guild_id, job_name, lvl, loon):
    db.execute("INSERT IGNORE INTO guildWorkPayouts (GuildID, JobNaam, UnlockLvl, Loon) VALUES (%s, %s, %s, %s)", guild_id, job_name, lvl, loon)


def reset_jobs(guild_id):
    db.execute("DELETE FROM guildWorkPayouts WHERE GuildID = %s", guild_id)


if __name__ == '__main__':
    print("This file is not meant to be running seperatly from the bot.py file.")
