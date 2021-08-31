from random import choice
from string import hexdigits

from lib.db import db


def general_checks(guild_id, user_id, bet, member_id=0):
    if not has_enough_balance(guild_id, user_id, bet):
        err_msg = "You don't have enough cash to play this minigame."
    elif user_id == member_id:
        err_msg = "You cannot play this game with yourself."
    else:
        err_msg = None
    return err_msg


# def check_bet(bet, min_bet, max_bet):
#     return True if max_bet >= bet >= min_bet else False
#
#
# def get_bets(guild_id, command):
#     all_bets = db.record("SELECT PayoutsCasino FROM guildPayouts WHERE GuildID = %s", guild_id)
#     bets = general.get_value(command.lower(), all_bets[0])
#     bet = bets.split(',')
#
#     if int(bet[0]) == 0:
#         bet[0] = 100
#
#     return int(bet[0]), int(bet[1])


def has_enough_balance(guild_id, user_id, bet):
    user_bal = db.record("SELECT cash FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)
    return True if int(user_bal[0]) >= bet else False


def create_token():
    return "".join([choice(hexdigits) for x in range(5)])


if __name__ == '__main__':
    print("This file is not meant to be running seperatly from the bot.py file.")
