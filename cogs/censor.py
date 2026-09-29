import re
import discord
from discord.ext import commands

ANYWHERE = ["fuck", "shit", "bitch"]
WHOLE_WORD = ["ass", "asses", "asshole", "assholes", "dumbass", "jackass", "badass"]
ALLOWED = ["bullshit"]

PATTERN = re.compile(
    "|".join(map(re.escape, ANYWHERE)) + r"|\b(" + "|".join(map(re.escape, WHOLE_WORD)) + r")\b",
    re.IGNORECASE
)
ALLOW = re.compile(r"\b(" + "|".join(map(re.escape, ALLOWED)) + r")\b", re.IGNORECASE)

class Censor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check(self, message):
        if message.author.bot or not message.guild:
            return
        cleaned = ALLOW.sub("", message.content)
        if PATTERN.search(cleaned):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention} said a bad language word",
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.check(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.check(after)

async def setup(bot):
    await bot.add_cog(Censor(bot))