import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def setup_hook():
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"Loaded {file}")
            except Exception as e:
                print(f"Skipped {file}: {e}")
    await bot.tree.sync()

@bot.event
async def on_ready():
    print(f"{bot.user} is online")

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run(TOKEN)