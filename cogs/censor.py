import re
import discord
from discord.ext import commands

BANNED_WORDS = ["fuck", "shit", "bitch"]
PATTERN = re.compile(r"\b(" + "|".join(map(re.escape, BANNED_WORDS)) + r")\b", re.IGNORECASE)

class Censor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        if message.author.guild_permissions.manage_messages:
            return
        if PATTERN.search(message.content):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, said a bad language word.",
                delete_after=5
            )

async def setup(bot):
    await bot.add_cog(Censor(bot))