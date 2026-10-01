import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

MODEL = "gemini-flash-latest"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
SYSTEM_PROMPT = "You are a gaming assistant for an esports team. Answer in a few sentences. If you aren't sure, say so."

class Ask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ask", description="Ask the bot about a game")
    @app_commands.checks.cooldown(1, 15)
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()

        key = os.getenv("GEMINI_API_KEY")
        if not key:
            await interaction.followup.send("No Gemini key found. Add GEMINI_API_KEY to .env.")
            return

        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": question}]}],
        }
        headers = {"x-goog-api-key": key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(GEMINI_URL, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    data = await resp.json()
                    if resp.status != 200:
                        msg = data.get("error", {}).get("message", "unknown error")
                        answer = f"Gemini error {resp.status}: {msg}"
                    else:
                        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            answer = "Gemini didn't send an answer back. It might have blocked the question."
        except Exception as e:
            answer = f"Couldn't reach Gemini: {e}"

        await interaction.followup.send(answer[:1900])

    async def cog_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Chill. Try again in {error.retry_after:.0f}s.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ask(bot))