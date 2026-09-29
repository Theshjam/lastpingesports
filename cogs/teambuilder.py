import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True   # needed to see reactions
intents.members = True     # needed to get full user info from reactions

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def maketeams(ctx, message_id: int, team_size: int, emoji: str = "✅"):
    """
    Usage: !maketeams <poll_message_id> <team_size> [emoji]
    Example: !maketeams 123456789012345678 3 ✅
    """
    try:
        poll_message = await ctx.channel.fetch_message(message_id)
    except discord.NotFound:
        await ctx.send("Couldn't find that message. Make sure the message ID is correct and it's in this channel.")
        return

    # Find the reaction matching the given emoji
    target_reaction = None
    for reaction in poll_message.reactions:
        if str(reaction.emoji) == emoji:
            target_reaction = reaction
            break

    if target_reaction is None:
        await ctx.send(f"No one has reacted with {emoji} yet.")
        return

    # Collect all users who reacted (excluding bots)
    users = [user async for user in target_reaction.users() if not user.bot]

    if len(users) == 0:
        await ctx.send("No participants found.")
        return

    # Shuffle randomly
    random.shuffle(users)

    # Split into teams of the given size
    teams = [users[i:i + team_size] for i in range(0, len(users), team_size)]

    # Build the response message
    response = f"**Teams (size {team_size}):**\n\n"
    for i, team in enumerate(teams, start=1):
        names = ", ".join(user.mention for user in team)
        response += f"**Team {i}:** {names}\n"

    await ctx.send(response)

bot.run("YOUR_BOT_TOKEN")