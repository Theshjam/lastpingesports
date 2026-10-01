import discord
from discord.ext import commands

def can_report(member):
    return member.guild_permissions.manage_guild or any(r.name == "Captain" for r in member.roles)

class Tournament:
    def __init__(self, entrants, on_finish):
        self.alive = entrants #who is still in the tournament
        self.round = 0
        self.byes = []
        self.matches = []
        self.winners = [] #stores who won each match in the current round
        self.round_closed = False
        self.cancelled = False
        self.on_finish = on_finish

    def build_round(self):
        self.round += 1
        n = len(self.alive)
        size = 1
        while size < n:
            size *= 2
        bye_count = size - n
        self.byes = self.alive[:bye_count]
        rest = self.alive[bye_count:]
        self.matches = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
        self.winners = [None] * len(self.matches)
        self.round_closed = False

    async def start_round(self, channel):
        self.build_round()
        header = f"__**Round {self.round}**__"
        if self.byes:
            header += "\nBye (auto advance): " + ", ".join(f"**{e['name']}**" for e in self.byes)
        await channel.send(header)
        for i, (a, b) in enumerate(self.matches):
            await channel.send(f"**Match {i + 1}:** {a['name']} vs {b['name']}", view=MatchView(self, i))

    async def advance_if_done(self, channel):
        if self.round_closed or any(w is None for w in self.winners):
            return
        self.round_closed = True
        self.alive = self.byes + self.winners
        if len(self.alive) == 1:
            champ = self.alive[0]
            mentions = ", ".join(m.mention for m in champ["members"])
            await channel.send(f"🏆 **{champ['name']}** wins the tournament! GG {mentions}")
            self.on_finish()
        else:
            await self.start_round(channel)

class MatchView(discord.ui.View):
    def __init__(self, tournament, index):
        super().__init__(timeout=None)
        self.tournament = tournament
        self.index = index
        for slot, entrant in enumerate(tournament.matches[index]):
            button = discord.ui.Button(label=f"{entrant['name']} wins"[:80], style=discord.ButtonStyle.primary)
            button.callback = self.make_callback(slot)
            self.add_item(button)

    def make_callback(self, slot):
        async def callback(interaction: discord.Interaction):
            t = self.tournament
            if t.cancelled:
                await interaction.response.send_message("This tournament was cancelled.", ephemeral=True)
                return
            if not can_report(interaction.user):
                await interaction.response.send_message("Only Captains or admins can report results.", ephemeral=True)
                return
            if t.winners[self.index] is not None:
                await interaction.response.send_message("Already reported.", ephemeral=True)
                return

            winner = t.matches[self.index][slot]
            t.winners[self.index] = winner
            for item in self.children:
                item.disabled = True
            self.stop()
            await interaction.response.edit_message(
                content=f"{interaction.message.content}\n✅ **{winner['name']}** advances", view=self
            )
            await t.advance_if_done(interaction.channel)
        return callback

class Bracket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}
        if not hasattr(bot, "entrants"):
            bot.entrants = {}

    @commands.command()
    async def bracket(self, ctx):
        """Builds a bracket from the last !teampoll or !solopoll in this channel."""
        if not can_report(ctx.author):
            await ctx.send("Only Captains or admins can start a tournament.")
            return
        if ctx.channel.id in self.active:
            await ctx.send("A tournament is already running here. Use `!endbracket` to cancel it.")
            return
        entrants = self.bot.entrants.get(ctx.channel.id)
        if not entrants or len(entrants) < 2:
            await ctx.send("Nothing to build a bracket from. Run `!teampoll` or `!solopoll` first.")
            return

        channel_id = ctx.channel.id
        t = Tournament(list(entrants), on_finish=lambda: self.active.pop(channel_id, None))
        self.active[channel_id] = t
        await ctx.send(f"🏆 **Tournament time. {len(entrants)} entrants.** Captains or admins, click the winner of each match.")
        await t.start_round(ctx.channel)

    @commands.command()
    async def endbracket(self, ctx):
        """Cancels the tournament running in this channel."""
        if not can_report(ctx.author):
            await ctx.send("Only Captains or admins can cancel a tournament.")
            return
        t = self.active.pop(ctx.channel.id, None)
        if t is None:
            await ctx.send("No tournament running here.")
            return
        t.cancelled = True
        await ctx.send("Tournament cancelled.")

async def setup(bot):
    await bot.add_cog(Bracket(bot))