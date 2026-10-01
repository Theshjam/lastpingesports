import discord
from discord.ext import commands

AUTO_ROLE = "Gamer"

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        role = discord.utils.get(member.guild.roles, name=AUTO_ROLE)
        if role is None:
            print(f"[welcome] No '{AUTO_ROLE}' role found in {member.guild.name}")
        else:
            try:
                await member.add_roles(role, reason="Auto role on join")
            except discord.Forbidden:
                print(f"[welcome] Can't assign '{AUTO_ROLE}'. Move the bot's role above it.")

        channel = discord.utils.get(member.guild.text_channels, name="welcome")
        if channel:
            await channel.send(f"Welcome to Last Ping Esports, {member.mention}. Try not to throw.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))