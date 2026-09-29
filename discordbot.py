import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
Guild_ID = os.getenv("GUILD_ID")

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
    guild = discord.Object(id=int(os.getenv("GUILD_ID")))
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

@bot.event
async def on_ready():
    print(f"{bot.user} is online")

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run(TOKEN)