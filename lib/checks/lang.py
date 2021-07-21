from lib.db import db
import json
from glob import glob

langs = [files.split('/')[-1][-7:-5].lower() for files in glob(f"./data/languages/lang_*.json")]


def get_lang(guild_id):
    lang = db.record("SELECT Lang FROM guilds WHERE GuildID = %s", guild_id)

    if lang is None:
        lang = ("en",)

    if lang[0] in langs:
        return lang[0]
    else:
        return "en"


def get_message(lang, message):
    file = open(f"data/languages/lang_{lang.upper()}.json", "r", encoding="utf-8")
    lang_file = json.load(file)
    file.close()

    try:
        return lang_file[message]
    except Exception:
        try:
            en_file = open(f"data/languages/lang_EN.json", "r", encoding="utf-8")
            en_lang_file = json.load(en_file)
            en_file.close()
            return en_lang_file[message]
        except Exception:
            return lang_file['LANG_Exception']


if __name__ == '__main__':
    print("This file is not meant to be running seperatly from the bot.py file.")
