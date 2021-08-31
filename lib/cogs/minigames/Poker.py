import json
from asyncio import TimeoutError
from random import choice

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, minigames

COMMAND = "poker"


class Poker(Cog):
    EMOTES = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

    def __init__(self, bot):
        self.bot = bot

        file = open(f"data/extra/card_deck.json", "r", encoding="utf-8")
        self.cards = json.load(file)
        file.close()

    def create_embed(self, ctx, cards, profit, currency, desc, color=Color.blue()):
        embed = Embed(description=desc, color=color)
        embed.add_field(name="Your Hand", value=f"".join([str(item) for item in cards]), inline=True)
        embed.add_field(name="Profit", value=f"{currency}{profit}", inline=True)
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    @staticmethod
    def draw_card(deck):
        return choice(deck)

    @staticmethod
    async def get_emotes(ctx, message_id):
        msg = await ctx.channel.fetch_message(message_id)
        emote_list = [0, 0, 0, 0, 0]

        index = 0
        for reaction in msg.reactions:
            if reaction.count > 1:
                users = await reaction.users().flatten()
                for user in users:
                    if user.id == ctx.author.id:
                        emote_list[index] = 1
            index += 1
        return emote_list

    def check_game(self, hand):
        user_won = True
        if self.check_royal_flush(hand):
            ending = "Royal Flush"
            multiplier = 15
        elif self.check_straight_flush(hand):
            ending = "Straight Flush"
            multiplier = 12
        elif self.check_four_of_a_kind(hand):
            ending = "Four of a Kind"
            multiplier = 10
        elif self.check_full_house(hand):
            ending = "Full House"
            multiplier = 8
        elif self.check_flush(hand):
            ending = "Flush"
            multiplier = 6
        elif self.check_straight(hand):
            ending = "Straight"
            multiplier = 4
        elif self.check_three_of_a_kind(hand):
            ending = "Three of a Kind"
            multiplier = 3
        elif self.check_two_pair(hand):
            ending = "Two Pair"
            multiplier = 2
        elif self.check_pair(hand):
            ending = "One Pair"
            multiplier = 1.5
        else:
            user_won = False
            ending = None
            multiplier = 0

        return user_won, ending, multiplier

    @staticmethod
    def get_cards(hand):
        cards = []
        for card in hand:
            cards.append(card[:-1])
        return cards

    @staticmethod
    def convert_emotes_to_cards(hand):
        cards = []
        for card in hand:
            card = card.split(':')[1]
            value = card[:-1]
            if value == 'j':
                value = 11
            elif value == 'q':
                value = 12
            elif value == 'k':
                value = 13
            elif value == 'Ace':
                value = 14
            cards.append(str(value) + card[-1])
        return cards

    @staticmethod
    def get_values(hand):
        values = []
        for card in hand:
            values.append(int(card[:-1]))
        return values

    @staticmethod
    def is_sequential(values):
        values.sort()

        if values[-1] == 14 and values[0] == 2:
            values.insert(0, 1)
            values.pop()

        previous_number = values[0] - 1
        for value in values:
            if value == previous_number + 1:
                previous_number = value
            else:
                return False
        return True

    @staticmethod
    def check_royal_flush(hand):
        suit = hand[0][-1]
        req = ['10', '11', '12', '13', '14']

        for card in hand:
            if card[:-1] in req and card[-1] == suit:
                pass
            else:
                return False
        return True

    def check_straight_flush(self, hand):
        suit = hand[0][-1]

        for card in hand:
            if card[-1] != suit:
                return False
        return self.is_sequential(self.get_values(hand))

    def check_four_of_a_kind(self, hand):
        cards = self.get_cards(hand)
        duplicates = {i: cards.count(i) for i in cards}
        for duplicate in duplicates:
            if duplicates[duplicate] == 4:
                return True
        return False

    def check_full_house(self, hand):
        cards = self.get_cards(hand)
        duplicates = {i: cards.count(i) for i in cards}
        for duplicate in duplicates:
            if duplicates[duplicate] == 3 or duplicates[duplicate] == 2:
                pass
            else:
                return False
        return True

    @staticmethod
    def check_flush(hand):
        suit = hand[0][-1]
        for card in hand:
            if card[-1] != suit:
                return False
        return True

    def check_straight(self, hand):
        return self.is_sequential(self.get_values(hand))

    def check_three_of_a_kind(self, hand):
        cards = self.get_cards(hand)
        duplicates = {i: cards.count(i) for i in cards}
        for duplicate in duplicates:
            if duplicates[duplicate] == 3:
                return True
        return False

    def check_two_pair(self, hand):
        pairs = 0
        cards = self.get_cards(hand)
        duplicates = {i: cards.count(i) for i in cards}
        for duplicate in duplicates:
            if duplicates[duplicate] == 2:
                pairs += 1

        if pairs == 2:
            return True
        else:
            return False

    def check_pair(self, hand):
        cards = self.get_cards(hand)
        duplicates = {i: cards.count(i) for i in cards}
        for duplicate in duplicates:
            if duplicates[duplicate] == 2:
                return True
        return False

    @command(name="poker")
    @cooldown(3, 3600, BucketType.user)
    async def poker(self, ctx, bet: int):
        """
        Be a real BALR and play poker.
        /Examples/ `poker 500`
        /Multipliers/ 15x - Royal Flush\n12x - Straight Flush\n10x - Four of a Kind\n8x - Full House\n6x - Flush\n4x - Straight\n3x - Three of a kind\n2x - Two Pair\n1.5x - One Pair
        """
        currency = general.get_currency(ctx.guild.id)
        err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet)

        if err_msg is not None:
            await ctx.send(err_msg)
            return

        general.remove_money(ctx.guild.id, ctx.author.id, bet)
        player_hand = []
        deck = self.cards["deck"]

        for i in range(5):
            card = self.draw_card(deck)
            deck.remove(card)
            player_hand.append(card["emote"])

        desc = "`draw` to reroll unlocked cards.\nUse reactions to lock cards."
        embed = self.create_embed(ctx, player_hand, bet, currency, desc)
        message = await ctx.send(embed=embed)

        for emote in self.EMOTES:
            await message.add_reaction(emote)

        def check(m):
            return m.author == ctx.author and m.content.lower() == "draw"

        try:
            await self.bot.wait_for('message', check=check, timeout=30)
            locked_cards = await self.get_emotes(ctx, message.id)

            x = 0
            while x < len(player_hand):
                if locked_cards[x] == 0:
                    player_hand.remove(player_hand[x])
                    card = self.draw_card(deck)
                    deck.remove(card)
                    player_hand.insert(x, card["emote"])
                x += 1

            player_cards = self.convert_emotes_to_cards(player_hand)
            user_won, ending, multiplier = self.check_game(player_cards)

            if user_won:
                await message.edit(embed=self.create_embed(ctx, player_hand, int(bet * multiplier), currency, f"You Won: **{ending}**", Color.green()))
                general.add_money(ctx.guild.id, ctx.author.id, int(bet * multiplier))
            else:
                await message.edit(embed=self.create_embed(ctx, player_hand, -bet, currency, f"You Lost {currency}{bet}.", Color.red()))
        except TimeoutError:
            await message.edit(embed=self.create_embed(ctx, player_hand, -bet, currency, "I got no responds. The command is cancelled.", Color.red()))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Poker(bot))
