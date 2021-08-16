from discord import Embed, Color
from discord.ext.commands import Cog, command, cooldown, BucketType

from lib.checks import general, lang
from lib.db import db


class HelpCmd(Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, ctx, cmd):
        prefix = db.record("SELECT Prefix FROM guilds WHERE GuildID = %s", ctx.guild.id)

        if cmd.help is None:
            help_desc = ["No Description."]
        else:
            help_desc = cmd.help.split('/')

        embed = Embed(
            description=help_desc[0],
            color=Color.blue()
        )
        parameters = []
        for key, value in cmd.clean_params.items():
            parameters.append(f" [{key}]" if '=' in str(value) else f" <{key}>")

        embed.add_field(name="Command Usage", value=f"`{prefix[0]}{cmd}" + "".join(parameters) + "`", inline=False)

        if cmd.aliases:
            embed.add_field(name="Aliases", value=", ".join([f"`{alias}`" for alias in cmd.aliases]))

        index = 1
        fields = []
        while index < len(help_desc) - 1:
            fields.append({"name": help_desc[index], "value": self.replace_placeholders(ctx.guild.id, cmd, help_desc[index + 1])})
            index += 2

        for field in fields:
            embed.add_field(name=field['name'], value=field['value'], inline=False)

        embed.set_footer(text=self.bot.FOOTER)
        embed.set_author(name=f"Help: {str(cmd).title()}", icon_url=f"{self.bot.user.avatar_url}")
        return embed

    @staticmethod
    def get_payouts(table, cmd, guild_id):
        payouts = db.record(f"SELECT {table} FROM guildPayouts WHERE GuildID = %s", guild_id)
        payout = general.get_value(str(cmd).lower(), payouts[0])
        payout = payout.split(',')
        return payout[0], payout[1]

    def replace_placeholders(self, guild_id, cmd, value):
        currency = db.record("SELECT Currency FROM guilds WHERE GuildID = %s", guild_id)

        failrates = db.record("SELECT Failrates FROM guilds WHERE GuildID = %s", guild_id)
        failrate = general.get_value(str(cmd).lower(), failrates[0])

        if str(cmd).lower() in ['beg', 'crime', 'fish']:
            min_payout, max_payout = self.get_payouts("Payouts", cmd, guild_id)
        else:
            min_payout, max_payout = self.get_payouts("PayoutsCasino", cmd, guild_id)
            min_payout = self.bot.MIN_BET

        value = value.replace('%CURRENCY%', f'{currency[0]}')
        value = value.replace('%MIN%', f'{min_payout}')
        value = value.replace('%MAX%', f'{max_payout}')
        value = value.replace('%FAIL%', f'{failrate}%')
        value = value.replace('%JOBS%', f'COMING SOON')
        return value

    def get_command(self, cmd_name):
        correct_command = "no-cmd"

        for cmd in self.bot.COMMANDS:
            if isinstance(cmd, dict):
                if cmd_name == cmd['name']:
                    correct_command = cmd['name']
                elif cmd_name in cmd['aliases']:
                    correct_command = cmd['name']
            elif cmd_name == cmd:
                correct_command = cmd

            if correct_command != "no-cmd":
                break
        return self.bot.get_command(correct_command)

    @command(name="help", aliases=["commands"])
    @cooldown(1, 2, BucketType.user)
    async def helpcmd(self, ctx, *cmd):
        """Get help with every command."""
        if cmd == ():
            prefix = db.record("SELECT Prefix FROM guilds WHERE GuildID = %s", ctx.guild.id)
            embed = Embed(
                description=f"{lang.get_message(ctx.language, 'HELP_CommandUsage')}: `{prefix[0]}help <command>`",
                color=Color.blue()
            )
            embed.add_field(name="General Commands", value="`help`, `rank`, `levels`, `user-info`, `guild-info`, `reset`, `dashboard`, `source`, `invite`, `ping`, `stats`", inline=False)
            embed.add_field(name="Economy Commands", value="`eco`, `beg`, `crime`, `fish`, `inventory`, `balance`, `deposit`, `withdraw`, `pay`, `request`, `social`, `work`, `job`, `shop`, `animal`", inline=False)
            embed.add_field(name="Minigame Commands", value="`blackjack`, `roulette`, `slots`, `coinflip`, `crash`, `horse`, `russian-roulette`, `poker`, `higher-lower`, `tictactoe`", inline=False)
            embed.set_footer(text=self.bot.FOOTER)
            embed.set_author(name="Help", icon_url=f"{self.bot.user.avatar_url}")
            await ctx.send(embed=embed)
        else:
            cog_cmd = self.get_command("-".join(cmd).lower())
            if cog_cmd is None:
                await ctx.send(lang.get_message(ctx.language, 'HELP_404'))
            else:
                await ctx.send(embed=self.create_embed(ctx, cog_cmd))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Help")


def setup(bot):
    bot.add_cog(HelpCmd(bot))
