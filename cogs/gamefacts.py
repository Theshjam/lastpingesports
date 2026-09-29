import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

class Ask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ask", description="Ask the bot about a game")
    @app_commands.checks.cooldown(1, 15)
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        payload = {
            "model": MODEL,
            "prompt": f"You are a gaming assistant for an esports team. Answer in a few sentences. If you aren't sure, say so.\n\nQuestion: {question}",
            "stream": False,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(OLLAMA_URL, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    data = await resp.json()
            answer = data.get("response", "No answer came back.")
        except Exception as e:
            answer = f"Couldn't reach Ollama: {e}"
        await interaction.followup.send(answer[:1900])

    async def cog_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Chill. Try again in {error.retry_after:.0f}s.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ask(bot))