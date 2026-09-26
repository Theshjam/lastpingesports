import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name="Member")
        if role:
            await member.add_roles(role)
        channel = discord.utils.get(member.guild.text_channels, name="welcome")
        if channel:
            await channel.send(f"Welcome to Last Ping Esports, {member.mention}. Try not to throw.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))

    