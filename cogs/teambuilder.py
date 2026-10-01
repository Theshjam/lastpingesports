import random
import asyncio
import discord
from discord.ext import commands

class PlayPoll(discord.ui.View):
    def __init__(self, question):
        super().__init__(timeout=None)
        self.question = question
        self.players = {}

    def render(self, closed=False):
        status = "🔒 Poll closed" if closed else "Tap the button to join or leave"
        names = "\n".join(m.mention for m in self.players.values()) or "Nobody yet"
        return f"📊 **{self.question}**\n{status}\n\n**Playing ({len(self.players)}):**\n{names}"

    @discord.ui.button(label="I'm playing", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.players:
            del self.players[interaction.user.id]
        else:
            self.players[interaction.user.id] = interaction.user
        await interaction.response.edit_message(content=self.render(), view=self)

class Teams(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "entrants"):
            bot.entrants = {}

    async def run_poll(self, ctx, minutes, question):
        if minutes < 1:
            await ctx.send("Poll has to run at least 1 minute.")
            return None
        view = PlayPoll(question)
        poll_msg = await ctx.send(view.render(), view=view)

        await asyncio.sleep(minutes * 60)

        for item in view.children:
            item.disabled = True
        view.stop()
        await poll_msg.edit(content=view.render(closed=True), view=view)

        players = list(view.players.values())
        if len(players) < 2:
            await ctx.send("Not enough players. Y'all are soft.")
            return None
        random.shuffle(players)
        return players

    @commands.command()
    async def teampoll(self, ctx, minutes: int, num_teams: int, *, question: str = "Who's playing?"):
        """Usage: !teampoll 2 4 Scrims tonight?"""
        if num_teams < 2:
            await ctx.send("You need at least 2 teams.")
            return
        players = await self.run_poll(ctx, minutes, question)
        if not players:
            return

        num_teams = min(num_teams, len(players))
        teams = [players[i::num_teams] for i in range(num_teams)]
        entrants = [{"name": f"Team {i}", "members": team} for i, team in enumerate(teams, start=1)]
        self.bot.entrants[ctx.channel.id] = entrants

        lines = [f"**{e['name']}:** {', '.join(m.mention for m in e['members'])}" for e in entrants]
        await ctx.send("**Teams:**\n" + "\n".join(lines) + "\n\nRun `!bracket` to start a tournament.")

    @commands.command()
    async def solopoll(self, ctx, minutes: int, *, question: str = "Who's down for 1v1s?"):
        """Usage: !solopoll 2 1v1 tournament?"""
        players = await self.run_poll(ctx, minutes, question)
        if not players:
            return

        entrants = [{"name": m.display_name, "members": [m]} for m in players]
        self.bot.entrants[ctx.channel.id] = entrants

        names = ", ".join(m.mention for m in players)
        await ctx.send(f"**{len(players)} players locked in:** {names}\n\nRun `!bracket` to start a tournament.")

async def setup(bot):
    await bot.add_cog(Teams(bot))