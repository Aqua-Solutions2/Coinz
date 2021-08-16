from lib.db import db

DEFAULT = ((0, 0, "Cashier", 0, 210),
           (0, 0, "Janitor", 0, 250),
           (0, 0, "Housekeeper", 0, 280),
           (0, 0, "Teacher", 0, 340),
           (0, 0, "Construction Worker", 0, 390),
           (0, 0, "Mechanic", 0, 460),
           (0, 0, "Electrician", 0, 490),
           (0, 0, "Police Officer", 0, 550),
           (0, 0, "Lawyer", 0, 680),
           (0, 0, "Software Developer", 0, 720),
           (0, 0, "Dentist", 0, 800))


def get_jobs(guild_id):
    all_jobs = db.records("SELECT * FROM guildWorkPayouts WHERE GuildID = %s", guild_id)
    return DEFAULT if all_jobs == () else all_jobs


def set_job(guild_id, job_name, lvl, loon):
    db.execute("INSERT IGNORE INTO guildWorkPayouts (GuildID, JobNaam, UnlockLvl, Loon) VALUES (%s, %s, %s, %s)", guild_id, job_name, lvl, loon)


def reset_jobs(guild_id):
    db.execute("DELETE FROM guildWorkPayouts WHERE GuildID = %s", guild_id)


if __name__ == '__main__':
    print("This file is not meant to be running seperatly from the bot.py file.")
