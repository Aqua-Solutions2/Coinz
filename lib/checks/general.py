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
    db.execute("INSERT IGNORE INTO userData (GuildId, UserID) VALUES (%s, %s)", guild_id, user_id)

#
# def has_enough_balance(guild_id, user_id, req_bal):
#     bal = db.record("SELECT cash FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)
#
#     if bal is None:
#         return False
#     else:
#         bal = bal[0]
#
#     if bal >= req_bal:
#         return True
#     else:
#         return False


def has_failed(guild_id, command):
    failrates = db.record(f"SELECT Failrates FROM guilds WHERE GuildID = %s", guild_id)
    failrate = get_value(command.lower(), failrates[0])

    number = randint(1, 100)
    if number >= failrate:
        return False
    else:
        return True


def get_quantity(inv):
    fishing_rod = lock = gun = bomb = 0

    if inv != ("",):
        items = inv[0].split('|')
        for item in items:
            if item.startswith('fishing_rod'):
                fishing_rod = 1
            elif item.startswith('gun'):
                gun = 1
            elif item.startswith('lock'):
                lock = 1
            elif item.startswith('bomb'):
                item, quantity = item.split('*')
                bomb = quantity

    return fishing_rod, lock, gun, bomb


def extra_rob(guild_id, user_id):
    user_inv = db.record("SELECT Inventory FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)
    rod, lock, gun, bomb = get_quantity(user_inv)
    return (lock * 5) + (gun * 10) + bomb


def check_status(guild_id, command):
    statusses = db.record(f"SELECT DisabledCommands FROM guilds WHERE GuildID = %s", guild_id)
    return True if command.lower() not in statusses[0].split(',') else False


def get_currency(guild_id):
    return db.record("SELECT Currency FROM guilds WHERE GuildID = %s", guild_id)[0]


def get_payout(guild_id, command, type_="Payouts"):
    payouts = db.record(f"SELECT {type_} FROM guildPayouts WHERE GuildID = %s", guild_id)
    payout = get_value(command, payouts)
    payout = payout.split(',')
    return randint(payout[0], payout[1])


def get_random_sentence(file, guild_id=0, payout=0):
    file = open(f'data/sentences/{file}.txt', 'r')
    sentences = file.readlines()
    file.close()

    sentence = choice([x.replace('\n', '') for x in sentences])
    sentence = sentence.replace('%CURRENCY%', str(get_currency(guild_id)))
    sentence = sentence.replace('%MONEY%', str(payout))
    return sentence


def add_money(guild_id, user_id, money):
    db.execute("UPDATE userData SET cash = cash + %s, netto = netto + %s WHERE GuildID = %s AND UserID = %s", money, money, guild_id, user_id)


def remove_money(guild_id, user_id, money):
    db.execute("UPDATE userData SET cash = cash - %s, netto = netto - %s WHERE GuildID = %s AND UserID = %s", money, money, guild_id, user_id)


def check_money(money):
    return True if 1 <= money <= max_balance else False


def check_balance(guild_id, user_id, amount):
    amount = abs(amount)
    bal = db.record("SELECT netto FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)

    if bal[0] + amount > max_balance:
        return abs(max_balance - bal[0])
    elif bal[0] - amount < min_balance:
        return abs(abs(bal[0]) - abs(min_balance))
    else:
        return amount


if __name__ == '__main__':
    print("This file is not meant to be running seperatly from the bot.py file.")
