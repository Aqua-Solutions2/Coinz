from lib.db import db
from lib.checks import general


def general_checks(guild_id, user_id, bet, command):
    min_bet, max_bet = get_bets(guild_id, command)

    if not check_bet(bet, min_bet, max_bet):
        err_msg = 'MINIGAMES_BetInvalid'
    elif not has_enough_balance(guild_id, user_id, bet):
        err_msg = 'MINIGAMES_NotEnoughBalance'
    else:
        err_msg = None
    return err_msg


def check_bet(bet, min_bet, max_bet):
    return True if max_bet >= bet >= min_bet else False


def get_bets(guild_id, command):
    all_bets = db.record("SELECT PayoutsCasino FROM guildPayouts WHERE GuildID = %s", guild_id)
    bets = general.get_value(command.lower(), all_bets[0])
    bet = bets.split(',')

    if bet[0] == 0:
        bet[0] = 100

    return int(bet[0]), int(bet[1])


def has_enough_balance(guild_id, user_id, bet):
    user_bal = db.record("SELECT cash FROM userData WHERE GuildID = %s AND UserID = %s", guild_id, user_id)
    return True if int(user_bal[0]) >= bet else False


if __name__ == '__main__':
    print("This file is not meant to be running seperatly from the bot.py file.")
