import itertools
import discord
from discord import app_commands
from discord.ext import commands

RESPONSES = [
    "Fuck off, we're busy.",
    "I never listened to your lectures anyway.",
    "What?",
    "Come again?",
    "You CAN'T get mad, William. You can't.",
    "Did we think before we typed?",
    "Deep breathes, William.",
    "A picture is worth a thousand words.",
    "Silence is powerful.",
    "Hard stuck Bronze behavior.",
    "Please make sure I have collaborator access to your opinion.",
    "Imagine typing that out and hitting send."
]

class TeacherJoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = True
        self.responses = itertools.cycle(RESPONSES)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.enabled or message.author.bot or not message.guild:
            return
        if any(role.name == "Teacher" for role in message.author.roles):
            try:
                await message.delete()
            except discord.NotFound:
                pass
            await message.channel.send(f"{message.author.mention} {next(self.responses)}")

    @app_commands.command(name="teachermode", description="Toggle the teacher joke")
    @app_commands.default_permissions(administrator=True)
    async def teachermode(self, interaction: discord.Interaction):
        self.enabled = not self.enabled
        state = "on" if self.enabled else "off"
        await interaction.response.send_message(f"Teacher mode is {state}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TeacherJoke(bot))