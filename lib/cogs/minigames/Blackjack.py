import json
from asyncio import TimeoutError
from random import choice

from discord import Embed, Color
from discord.ext.commands import command, Cog, BucketType, cooldown

from lib.checks import general, minigames

COMMAND = "blackjack"


class Blackjack(Cog):
    VALID_MESSAGES = ['hit', 'double down', 'pass']
    DEFAULT_CARD = "<:HiddenCard:866347556355178557>"

    def __init__(self, bot):
        self.bot = bot

        file = open(f"data/extra/card_deck.json", "r", encoding="utf-8")
        cards = json.load(file)
        file.close()

        self.DECK = cards["deck"]

    def create_embed(self, ctx, desc, player_cards, dealer_cards, player_values, dealer_values, color=Color.blue()):
        embed = Embed(description=desc, color=color)
        embed.add_field(
            name="Your Cards",
            value=f"".join([str(item) for item in player_cards]) + f"\n\nValue: {self.calc_total_value(player_values)}",
            inline=True
        )
        embed.add_field(
            name="Cards Dealer",
            value=f"".join([str(item) for item in dealer_cards]) + f"\n\nValue: {self.calc_total_value(dealer_values)}",
            inline=True
        )
        embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    def draw_card(self, cards, values):
        card = choice(self.DECK)
        emote = card['emote']
        value = card['values']

        if self.calc_total_value(values) + value > 21 and "ace" in emote.lower():
            value = 1

        cards.append(emote)
        values.append(value)
        return cards, values

    @staticmethod
    def calc_total_value(values):
        return sum(values)

    def game_status(self, player_values, dealer_values, end_game=False):
        player_value = self.calc_total_value(player_values)
        dealer_value = self.calc_total_value(dealer_values)

        if player_value > 21:
            status = "lost"
        elif player_value == 21 and dealer_value != 21:
            status = "won"
        elif dealer_value > 21:
            status = "won"
        elif player_value == 21 and dealer_value == 21:
            status = "tie"
        else:
            if end_game:
                distance_player = 21 - player_value
                distance_dealer = 21 - dealer_value

                if distance_player == distance_dealer:
                    status = "tie"
                elif distance_player > distance_dealer:
                    status = "lost"
                else:
                    status = "won"
            else:
                status = None
        return status

    @staticmethod
    def get_end_message(ctx, status, currency, bet):
        if status == 'lost':
            desc = "You lost from the dealer and lost %s%s." % (currency, bet)
            color = Color.red()
        elif status == 'tie':
            desc = "Tie. You got your bet back."
            color = Color.blue()
            general.add_money(ctx.guild.id, ctx.author.id, bet)
        else:
            desc = "You beat the dealer and won %s%s." % (currency, int(bet * 1.5))
            color = Color.green()
            general.add_money(ctx.guild.id, ctx.author.id, int(bet * 1.5))
        return desc, color

    def finish_dealer_cards(self, dealer_cards, dealer_values):
        while self.calc_total_value(dealer_values) < 17:
            dealer_cards, dealer_values = self.draw_card(dealer_cards, dealer_values)
        return dealer_cards, dealer_values

    @command(name="blackjack", aliases=["bj"])
    @cooldown(4, 3600, BucketType.user)
    async def blackjack(self, ctx, bet: int):
        """
        Play a game of blackjack to get some money. Blackjack pays 3 to 2.
        To win the game you have to beat the dealer's hand, without getting over 21 in total.
        /Example/ `blackjack 500`
        """
        currency = general.get_currency(ctx.guild.id)
        err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet)

        if err_msg is not None:
            await ctx.send(err_msg)
            return

        default_desc = "`hit` - Take another card.\n`stand` - End the game.\n`double down` - Double your bet, hit once, then stand."
        player_cards = []
        player_values = []
        dealer_cards = []
        dealer_values = []
        stop_game = False
        round_ = 0

        general.remove_money(ctx.guild.id, ctx.author.id, bet)
        player_cards, player_values = self.draw_card(player_cards, player_values)
        player_cards, player_values = self.draw_card(player_cards, player_values)
        dealer_cards, dealer_values = self.draw_card(dealer_cards, dealer_values)
        dealer_cards.append(self.DEFAULT_CARD)

        embed = self.create_embed(ctx, default_desc, player_cards, dealer_cards, player_values, dealer_values)
        message = await ctx.send(embed=embed)
        dealer_cards.pop()

        def check(m):
            return m.author == ctx.author and m.content.lower() in self.VALID_MESSAGES

        while True:
            status = self.game_status(player_values, dealer_values, end_game=True if stop_game else False)
            if status is not None:
                dealer_cards, dealer_values = self.finish_dealer_cards(dealer_cards, dealer_values)
                desc, color = self.get_end_message(ctx, status, currency, bet)
                await message.edit(embed=self.create_embed(ctx, desc, player_cards, dealer_cards, player_values, dealer_values, color))
                break
            else:
                if round_ > 0:
                    await message.edit(embed=self.create_embed(ctx, default_desc, player_cards, dealer_cards, player_values, dealer_values))

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30)

                if msg.content == self.VALID_MESSAGES[0]:
                    player_cards, player_values = self.draw_card(player_cards, player_values)
                    if self.calc_total_value(dealer_values) < 17:
                        dealer_cards, dealer_values = self.draw_card(dealer_cards, dealer_values)
                else:
                    stop_game = True
                    if msg.content == self.VALID_MESSAGES[1]:
                        general.remove_money(ctx.guild.id, ctx.author.id, bet)
                        bet = bet * 2
                        player_cards, player_values = self.draw_card(player_cards, player_values)
                round_ += 1
            except TimeoutError:
                embed = Embed(description="I got no responds. The command is cancelled.", color=Color.red())
                embed.set_author(name=COMMAND.title(), icon_url=f"{ctx.author.avatar_url}")
                embed.set_footer(text=self.bot.FOOTER)
                await message.edit(embed=embed)
                break

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COMMAND.title())


def setup(bot):
    bot.add_cog(Blackjack(bot))
