import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def startpoll(ctx, minutes: int, *, question: str):
    """
    Usage: !startpoll 5 Are you playing tonight?
    """
    poll_message = await ctx.send(
        f"📊 **{question}**\nReact with ✅ to join! (Poll closes in {minutes} minute(s))"
    )
    await poll_message.add_reaction("✅")

    # Save this poll's ID so !maketeams can find it automatically
    bot.last_poll_id = poll_message.id

    await asyncio.sleep(minutes * 60)

    await ctx.send("⏰ Poll closed! Use `!maketeams <team_size>` to make teams.")


@bot.command()
async def maketeams(ctx, team_size: int):
    """
    Usage: !maketeams 3
    """
    if not hasattr(bot, 'last_poll_id'):
        await ctx.send("No poll has been created yet! Use `!startpoll` first.")
        return

    try:
        poll_message = await ctx.channel.fetch_message(bot.last_poll_id)
    except discord.NotFound:
        await ctx.send("Couldn't find the poll message anymore.")
        return

    target_reaction = None
    for reaction in poll_message.reactions:
        if str(reaction.emoji) == "✅":
            target_reaction = reaction
            break

    if target_reaction is None:
        await ctx.send("No one has reacted to the poll yet.")
        return

    users = [user async for user in target_reaction.users() if not user.bot]

    if len(users) == 0:
        await ctx.send("No participants found.")
        return

    random.shuffle(users)
    teams = [users[i:i + team_size] for i in range(0, len(users), team_size)]

    response = f"**Teams (size {team_size}):**\n\n"
    for i, team in enumerate(teams, start=1):
        names = ", ".join(user.mention for user in team)
        response += f"**Team {i}:** {names}\n"

    await ctx.send(response)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


bot.run("YOUR_BOT_TOKEN")