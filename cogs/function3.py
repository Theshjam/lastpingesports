import discord
from discord.ext import commands
import re

intents = discord.Intents.default()
intents.message_content = True  # MUST also enable this in the Developer Portal

bot = commands.Bot(command_prefix="!", intents=intents)

banned_words = ["fuck", "shit", "ass", "bitch"]

# Build a regex pattern that only matches whole words (fixes "class" containing "ass")
pattern = re.compile(r'\b(' + '|'.join(re.escape(w) for w in banned_words) + r')\b', re.IGNORECASE)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # ignore all bots, not just this one

    if pattern.search(message.content):
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention} sad a bad language word",
                delete_after=5
            )
        except discord.Forbidden:
            print("Bot lacks permission to delete messages in this channel.")
        return

    await bot.process_commands(message)

bot.run("YOUR_BOT_TOKEN")