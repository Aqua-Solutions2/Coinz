from random import randint, choice

from lib.db import db

max_balance = 1000000000000  # 1 Trillion
min_balance = -1000000  # 1 Million


def parse_str(string):
    return string.split('|')


def get_value(name, string):
    parsed_string = parse_str(string)

    for i in parsed_string:
        if i.startswith(name):
            name, value = i.split(':')
            return value
    return -1


def create_row(guild_id, user_id):
    userdata = db.record("SELECT RowID FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)
    if userdata is None:
        db.execute("INSERT INTO userData (GuildId, UserID) VALUES (%s, %s)", guild_id, user_id)


def command_is_disabled(guild_id, command):
    command_status = db.record(f"SELECT DisabledCommands FROM guilds WHERE GuildID = %s", guild_id)
    return True if command.name.lower() in command_status[0].split(',') else False


def get_currency(guild_id):
    return db.record("SELECT Currency FROM guilds WHERE GuildID = %s", guild_id)[0]


def has_failed(command):
    failrate = get_value(command.name.lower(), "beg:10|fish:5|crime:60|rob:40")
    return False if randint(1, 100) >= failrate else True


def get_lvl(exp):
    return int(exp / 100)


def get_random_sentence(file, guild_id=0, payout=0):
    file = open(f'data/sentences/{file}.txt', 'r')
    sentences = file.readlines()
    file.close()

    sentence = choice([x.replace('\n', '') for x in sentences])
    sentence = sentence.replace('%CURRENCY%', str(get_currency(guild_id)))
    sentence = sentence.replace('%MONEY%', str(payout))
    return sentence


def add_money(guild_id, user_id, money):
    db.execute("UPDATE userData SET cash = cash + %s, Net = Net + %s WHERE GuildID = %s AND UserID = %s", money, money, guild_id, user_id)


def remove_money(guild_id, user_id, money):
    db.execute("UPDATE userData SET cash = cash - %s, Net = Net - %s WHERE GuildID = %s AND UserID = %s", money, money, guild_id, user_id)


def check_money(money):
    return True if 1 <= money <= max_balance else False


def check_balance(guild_id, user_id, amount):
    amount = abs(amount)
    bal = db.record("SELECT Net FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)

    if bal[0] + amount > max_balance:
        return abs(max_balance - bal[0])
    elif bal[0] - amount < min_balance:
        return abs(abs(bal[0]) - abs(min_balance))
    else:
        return amount


if __name__ == '__main__':
    print("This file is not meant to be running seperatly from the bot.py file.")
