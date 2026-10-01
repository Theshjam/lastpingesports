import discord
from discord import app_commands
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    role = app_commands.Group(
        name="role",
        description="Add or remove roles",
        default_permissions=discord.Permissions(manage_roles=True),
        guild_only=True,
    )

    def check_problem(self, interaction, member, role):
        me = interaction.guild.me
        author = interaction.user
        is_owner = interaction.guild.owner_id == author.id

        if role.is_default():
            return "Can't touch @everyone."
        if role.managed:
            return f"{role.mention} belongs to a bot or integration. Discord won't let anyone hand it out."
        if role >= me.top_role:
            return f"{role.mention} is at or above my top role. Drag my role higher in Server Settings."
        if not is_owner and role >= author.top_role:
            return f"You can't manage {role.mention}. It's at or above your top role."
        if not is_owner and member != author and member.top_role >= author.top_role:
            return f"{member.mention} outranks or matches you. Nice try."
        return None

    @role.command(name="add", description="Give a member a role")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def add(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        problem = self.check_problem(interaction, member, role)
        if problem:
            return await interaction.response.send_message(problem, ephemeral=True)
        if role in member.roles:
            return await interaction.response.send_message(f"{member.mention} already has {role.mention}.", ephemeral=True)

        await member.add_roles(role, reason=f"{interaction.user} via /role add")
        await interaction.response.send_message(
            f"Gave {role.mention} to {member.mention}.",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @role.command(name="remove", description="Take a role from a member")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def remove(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        problem = self.check_problem(interaction, member, role)
        if problem:
            return await interaction.response.send_message(problem, ephemeral=True)
        if role not in member.roles:
            return await interaction.response.send_message(f"{member.mention} doesn't have {role.mention}.", ephemeral=True)

        await member.remove_roles(role, reason=f"{interaction.user} via /role remove")
        await interaction.response.send_message(
            f"Took {role.mention} from {member.mention}.",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    async def cog_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            msg = "You need Manage Roles for that."
        elif isinstance(getattr(error, "original", None), discord.Forbidden):
            msg = "Discord said no. Check that my role has Manage Roles and sits above that role."
        else:
            msg = f"Something broke: {error}"
        await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Roles(bot))