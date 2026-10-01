import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def build_embed(self, member):
        embed = discord.Embed(
            title="Last Ping Esports Bot",
            description="Slash commands start with `/`. The rest start with `!`.",
            color=discord.Color.red(),
        )

        slash = []
        for cmd in sorted(self.bot.tree.get_commands(), key=lambda c: c.name):
            perms = getattr(cmd, "default_permissions", None)
            if perms and not member.guild_permissions.is_superset(perms):
                continue
            slash.append(f"`/{cmd.name}` {cmd.description}")

        prefix = []
        for cmd in sorted(self.bot.commands, key=lambda c: c.name):
            if cmd.hidden:
                continue
            usage = f"!{cmd.name} {cmd.signature}".strip()
            desc = (cmd.help or "").split("\n")[0]
            if desc.lower().startswith("usage"):
                desc = ""
            prefix.append(f"`{usage}` {desc}".strip())

        if slash:
            embed.add_field(name="Slash commands", value="\n".join(slash)[:1024], inline=False)
        if prefix:
            embed.add_field(name="! commands", value="\n".join(prefix)[:1024], inline=False)
        embed.add_field(
            name="Automatic stuff",
            value="Welcome message and Gamer role when you join\nProfanity filter in every channel",
            inline=False,
        )
        embed.set_footer(text="Polls and brackets run on buttons once they start.")
        return embed

    @commands.command(name="help")
    async def help_prefix(self, ctx):
        """Shows this list"""
        await ctx.send(embed=self.build_embed(ctx.author))

    @app_commands.command(name="help", description="Show everything the bot can do")
    async def help_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.build_embed(interaction.user), ephemeral=True)

async def setup(bot):
    bot.remove_command("help")
    await bot.add_cog(Help(bot))