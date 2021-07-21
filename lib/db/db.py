from mysql.connector import connect
from apscheduler.triggers.cron import CronTrigger
import json

credentials = json.load(open("./lib/db/db_credentials.json", "r", encoding="utf-8"))
cxn = connect(host=credentials["host"], user=credentials["user"], passwd=credentials["password"], database=credentials["database"])
cur = cxn.cursor(buffered=True)


def commit():
    cxn.commit()


def autosave(sched):
    sched.add_job(commit, CronTrigger(second=0))


def close():
    cxn.close()


def field(command, *values):
    cur.execute(command, tuple(values))


def record(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchone()


def records(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchall()


def column(command, *values):
    cur.execute(command, tuple(values))
    return [item[0] for item in cur.fetchall()]


def execute(command, *values):
    cur.execute(command, tuple(values))
    commit()


def multiexec(command, valueset):
    cur.executemany(command, valueset)
    commit()
