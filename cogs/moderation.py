import datetime
import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def outranks(self, mod, target):
        return mod.top_role > target.top_role or mod == mod.guild.owner

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason given"):
        if not self.outranks(interaction.user, member):
            await interaction.response.send_message("They outrank you. Nice try.", ephemeral=True)
            return
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.mention}. Reason: {reason}")

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason given"):
        if not self.outranks(interaction.user, member):
            await interaction.response.send_message("They outrank you. Nice try.", ephemeral=True)
            return
        await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
        await interaction.response.send_message(f"Timed out {member.mention} for {minutes} min. Reason: {reason}")

    @app_commands.command(name="purge", description="Delete recent messages")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

    async def cog_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            msg = "You don't have permission to do that."
        else:
            msg = f"Something broke: {error}"
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))