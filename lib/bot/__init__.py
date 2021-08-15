import sys
import time
from asyncio import sleep
from datetime import datetime
from glob import glob
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents, ActivityType, Activity
from discord.errors import Forbidden
from discord.ext import commands

from ..checks import general, lang
from ..db import db

PREFIX = "?"
BOT_NAME = "Coinz"
OWNER_IDS = [643072638075273248]
SHARDS = 1
COGS = [f'{folder}.{path.split("/")[-1][:-3]}' for folder in [path.split("/")[-1] for path in glob(f"./lib/cogs/*") if not path.endswith('__pycache__')] for path in glob(f"./lib/cogs/{folder}/*.py")]


def get_prefix(client, message):
    prefix = db.record("SELECT Prefix FROM guilds WHERE GuildID = %s", message.guild.id)
    prefix = prefix or [PREFIX]
    return commands.when_mentioned_or(prefix[0])(client, message)


class Ready(object):
    START_LOADING_BAR = False
    WIDTH = 50

    def __init__(self):
        for cog in COGS:
            setattr(self, cog.split('.')[1], False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        self.print_loading_bar()

    def all_ready(self):
        return all(getattr(self, cog.split('.')[1]) for cog in COGS)

    def print_loading_bar(self):
        if not self.START_LOADING_BAR:
            sys.stdout.write(f"[{BOT_NAME}] Loading Cogs: [%s]" % (" " * self.WIDTH))
            sys.stdout.flush()
            sys.stdout.write("\b" * (self.WIDTH + 1))
            self.START_LOADING_BAR = True
        sys.stdout.write("=" * (self.WIDTH // len(COGS)))
        sys.stdout.flush()

    @staticmethod
    def end_loading_bar():
        sys.stdout.write("]\n")


class Bot(commands.AutoShardedBot):
    FOOTER = f"© {datetime.now().year} - {BOT_NAME}"
    WEBSITE = "https://www.coinzbot.xyz/"
    TABLES = ["guildPayouts", "guildWorkPayouts", "guilds", "userData"]
    MIN_BET = 100
    COMMANDS = []

    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.scheduler = AsyncIOScheduler()
        self.cwd = str(Path(__file__).parents[0])

        with open("./lib/bot/token.txt", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        user_file = open("./data/blacklist/users.txt", "r", encoding="utf-8")
        self.BLACKLIST_USERS = [line.replace('\n', '') for line in user_file]
        user_file.close()

        guilds_file = open("./data/blacklist/guilds.txt", "r", encoding="utf-8")
        self.BLACKLIST_GUILDS = [line.replace('\n', '') for line in guilds_file]
        guilds_file.close()

        db.autosave(self.scheduler)

        intents = Intents.default()
        intents.members = True

        super().__init__(command_prefix=get_prefix, shard_count=SHARDS, owner_ids=OWNER_IDS, strip_after_prefix=True, intents=intents)
        self.remove_command("help")

    @staticmethod
    def setup():
        for cog in COGS:
            try:
                bot.load_extension(f'lib.cogs.{cog}')
            except Exception as e:
                print(f"[{BOT_NAME}] Cog {cog}: Error occured while trying to load cog.")
                print(e)

    def update_db(self):
        db.multiexec("INSERT IGNORE INTO guilds (GuildID) VALUES (%s)", ((guild.id,) for guild in self.guilds))

        remove_guilds = []
        stored_guilds = db.column("SELECT GuildID from guilds")
        for stored_guild in stored_guilds:
            if stored_guild not in [guild.id for guild in self.guilds]:
                remove_guilds.append((stored_guild,))

        for table in self.TABLES:
            db.multiexec(f"DELETE FROM {table} WHERE GuildID = %s", remove_guilds)
        db.commit()

    def run(self):
        self.setup()
        print(f"[{BOT_NAME}] Trying to connect all shards to the Discord API...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=commands.Context)

        if ctx.command is not None and ctx.guild is not None:
            ctx.language = lang.get_lang(ctx.guild.id)
            if message.author.id in self.BLACKLIST_USERS:
                await ctx.send(f"{lang.get_message(ctx.language, 'INIT_UserBanned')} <{self.WEBSITE}>.")
            elif not self.ready:
                await ctx.send(lang.get_message(ctx.language, "INIT_StartingUp"))
            else:
                db.execute("INSERT IGNORE INTO guilds (GuildID) VALUES (%s)", ctx.guild.id)
                db.execute("INSERT IGNORE INTO guildPayouts (GuildID) VALUES (%s)", ctx.guild.id)
                general.create_row(ctx.guild.id, ctx.author.id)
                await self.invoke(ctx)

    @staticmethod
    async def on_shard_connect(shard_id):
        print(f"[{BOT_NAME}] Shard {shard_id + 1}/{SHARDS} connected to the Discord API.")

    @staticmethod
    async def on_shard_disconnect(shard_id):
        print(f"[{BOT_NAME}] Shard {shard_id + 1}/{SHARDS} disconnected from the Discord API.")

    async def on_error(self, event, *args, **kwargs):
        if event == "on_command_error":
            print(f"[{BOT_NAME}] Something went wrong...")
        raise

    async def on_command_error(self, ctx, error):
        ignored_errors = (commands.CommandNotFound,)

        if isinstance(error, ignored_errors):
            print("ignored_error")
            # return

        if isinstance(error, commands.CommandOnCooldown):
            cooldown = error.retry_after

            if cooldown <= 60:
                time_formatted = f"{round(cooldown, 1)}s"
            else:
                time_formatted = time.strftime('%-Hh %-Mm %-Ss', time.gmtime(cooldown))
            await ctx.send(":x: " + lang.get_message(ctx.language, 'ERR_OnCooldown') % time_formatted)
        elif isinstance(error, commands.BadArgument):
            prefix = db.record("SELECT Prefix FROM guilds WHERE GuildID = %s", ctx.guild.id)
            await ctx.send(lang.get_message(ctx.language, 'ERR_InvalidArgumentsSpecific') % f"{prefix[0]}help {ctx.command}")
        elif isinstance(error, commands.CheckFailure):
            print("checkfailure")
        elif isinstance(error, commands.MissingRequiredArgument):
            print("MissingRequiredArgument")
        elif isinstance(error, commands.MemberNotFound):
            print("membernotfound")
        elif isinstance(error, commands.ChannelNotFound):
            print("channelnotfound")
        elif isinstance(error, commands.RoleNotFound):
            print("rolenotfound")
        elif hasattr(error, "original"):
            if isinstance(error.original, Forbidden):
                print("forbidden")
            else:
                raise error.original
        else:
            raise error

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            self.update_db()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)
            self.ready = True
            self.cogs_ready.end_loading_bar()

            for cmd in self.commands:
                if not cmd.aliases:
                    new_cmd = cmd.name
                else:
                    new_cmd = {
                        "name": cmd.name.lower(),
                        "aliases": [alias.lower() for alias in cmd.aliases]
                    }
                self.COMMANDS.append(new_cmd)

            await bot.change_presence(activity=Activity(type=ActivityType.watching, name="Elon Musk. | ?help"))

            print(f"[{BOT_NAME}] The bot is ready to use. (TOTAL SHARDS: {SHARDS})")
        else:
            print(f"[{BOT_NAME}] A shard reconnected to the Discord API.")

    async def on_message(self, message):
        await self.process_commands(message)


bot = Bot()
