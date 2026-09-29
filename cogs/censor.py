import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

# List of banned words/phrases (lowercase for easy matching)
banned_words = ["fuck", "shit", "bitch", "ass"]

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself (prevents infinite loops)
    if message.author == bot.user:
        return

    # Check if any banned word appears in the message
    if any(word in message.content.lower() for word in banned_words):
        await message.delete()
        await message.channel.send(
            f"{message.author.mention} said a bad language word" 
        )
        return  # stop here so it doesn't also process as a command

    # Important: allows other commands to still work
    await bot.process_commands(message)

bot.run("YOUR_BOT_TOKEN")