from discord import Embed, Color, Member
from discord.ext.commands import command, Cog, BucketType, cooldown
from lib.checks import general, lang, minigames
from asyncio import TimeoutError

COMMAND = "Tic Tac Toe"


class TicTacToe(Cog):
    BOARD_WIDTH = 3
    EMPTY_EMOTE = ':white_large_square:'
    X_EMOTE = ':regional_indicator_x:'
    O_EMOTE = ':o2:'

    def __init__(self, bot):
        self.bot = bot

        self.winning_conditions = (
                [[(x, y) for y in range(self.BOARD_WIDTH)] for x in range(self.BOARD_WIDTH)] +  # horizontals
                [[(x, y) for x in range(self.BOARD_WIDTH)] for y in range(self.BOARD_WIDTH)] +  # verticals
                [[(d, d) for d in range(self.BOARD_WIDTH)]] +  # diagonal from top-left to bottom-right
                [[(2 - d, d) for d in range(self.BOARD_WIDTH)]]  # diagonal from top-right to bottom-left
        )

    @staticmethod
    def create_board(board_list):
        board = ""
        for item in board_list:
            for box in item:
                board += box
            board += "\n"
        return board

    def create_embed(self, ctx, desc, board, turn=None, winner=None, color=Color.blue()):
        embed = Embed(description=desc, color=color)
        embed.add_field(name=lang.get_message(ctx.language, 'TICTACTOE_Board'), value=self.create_board(board), inline=False)
        if turn is not None:
            embed.add_field(name=lang.get_message(ctx.language, 'MINIGAMES_Turn'), value=f"{turn}", inline=False)
        elif winner is not None:
            embed.add_field(name=lang.get_message(ctx.language, 'MINIGAMES_Winner'), value=f"{winner}", inline=False)
        embed.set_author(name=COMMAND, icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    def create_no_responds(self, ctx):
        embed = Embed(description=lang.get_message(ctx.language, 'CMD_NoResponds'), color=Color.red())
        embed.set_author(name=COMMAND, icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=self.bot.FOOTER)
        return embed

    def get_winner(self, board):
        for positions in self.winning_conditions:
            values = [board[x][y] for (x, y) in positions]
            if len(set(values)) == 1 and values[0]:
                return values[0]

    @command(name="tictactoe", aliases=["tic-tac-toe", "ttt"])
    @cooldown(2, 3600, BucketType.user)
    async def tictactoe(self, ctx, member: Member, bet: int):
        if general.check_status(ctx.guild.id, "tictactoe"):
            err_msg = minigames.general_checks(ctx.guild.id, ctx.author.id, bet, "tictactoe", member.id)

            if err_msg is not None:
                await ctx.send(lang.get_message(ctx.language, err_msg))
                return

            board = [[self.EMPTY_EMOTE for x in range(self.BOARD_WIDTH)] for x in range(self.BOARD_WIDTH)]
            token = minigames.create_token()
            authors_turn = True
            turn = ctx.author
            currency = general.get_currency(ctx.guild.id)
            message = await ctx.send(content=f"{member.mention}", embed=self.create_embed(ctx, lang.get_message(ctx.language, 'MINIGAMES_Challenge') % (ctx.author.name, member.name, "Tic Tac Toe", member.name, token), board, turn.mention))

            def check_accept(m):
                return m.author == member and m.channel == ctx.channel and m.content == token

            try:
                await self.bot.wait_for('message', check=check_accept, timeout=60)

                general.create_row(ctx.guild.id, member.id)
                err_msg = minigames.general_checks(ctx.guild.id, member.id, bet, "tictactoe")

                if err_msg is not None:
                    await ctx.send(lang.get_message(ctx.language, err_msg))
                    return

                general.remove_money(ctx.guild.id, ctx.author.id, bet)
                general.remove_money(ctx.guild.id, member.id, bet)
            except TimeoutError:
                await message.edit(embed=self.create_no_responds(ctx))
                return

            await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'TICTACTOE_General') % int(self.BOARD_WIDTH ** 2), board, turn.mention))

            def check(m):
                return m.author == turn and m.channel == ctx.channel

            while True:
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=30)

                    try:
                        number = int(msg.content)
                        if not 1 <= number <= int(self.BOARD_WIDTH ** 2):
                            int("error")
                    except ValueError:
                        await ctx.send(lang.get_message(ctx.language, 'CMD_NumberExceedLimit') % (1, int(self.BOARD_WIDTH ** 2)))
                        continue

                    emote = self.X_EMOTE if authors_turn else self.O_EMOTE
                    index1 = int((number / self.BOARD_WIDTH) - 0.01)
                    index2 = number % self.BOARD_WIDTH - 1 if number % self.BOARD_WIDTH != 0 else self.BOARD_WIDTH-1

                    if board[index1][index2] == self.EMPTY_EMOTE:
                        board[index1][index2] = emote
                    else:
                        await ctx.send(lang.get_message(ctx.language, 'TICTACTOE_BoxFull'))

                    if all([True if self.EMPTY_EMOTE not in item else False for item in board]):
                        general.add_money(ctx.guild.id, ctx.author.id, bet)
                        general.add_money(ctx.guild.id, member.id, bet)
                        await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'MINIGAMES_TieMessage'), board, color=Color.red()))
                        break

                    winner = self.get_winner(board)
                    if winner == self.X_EMOTE:
                        general.add_money(ctx.guild.id, ctx.author.id, bet * 2)
                        await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'TICTACTOE_End') % (ctx.author.mention, currency, bet * 2), board, winner=ctx.author.mention, color=Color.green()))
                        break
                    elif winner == self.O_EMOTE:
                        general.add_money(ctx.guild.id, member.id, bet * 2)
                        await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'TICTACTOE_End') % (member.mention, currency, bet * 2), board, winner=member.mention, color=Color.green()))
                        break
                    else:
                        authors_turn = not authors_turn
                        turn = ctx.author if authors_turn else member
                        await message.edit(embed=self.create_embed(ctx, lang.get_message(ctx.language, 'TICTACTOE_General') % int(self.BOARD_WIDTH ** 2), board, turn.mention))
                except TimeoutError:
                    general.add_money(ctx.guild.id, member.id if authors_turn else ctx.author.id, bet)
                    await message.edit(embed=self.create_no_responds(ctx))
                    break
        else:
            ctx.command.reset_cooldown(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("TicTacToe")


def setup(bot):
    bot.add_cog(TicTacToe(bot))
