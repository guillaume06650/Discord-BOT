from discord.ext import commands, tasks
from discord.utils import *
import discord
import os
import random
import asyncio
import json
import urllib.request
from collections import defaultdict
from cat import Catfacts

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

bot.author_id = 228981978689437696  # Change to your discord id

message_counts = defaultdict(lambda: defaultdict(int))
message_timestamps = defaultdict(lambda: defaultdict(list))
active_polls = {}
minute_flood = 1
nb_messages = 7
flood_control = False

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def name(ctx):
    user_name = ctx.author.name
    await ctx.send(f'Your name is {user_name}')

@bot.command()
async def d6(ctx):
    roll = random.randint(1, 6)
    await ctx.send(f'You rolled a {roll} on a 6-sided die!')

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

@bot.command()
async def admin(ctx, member_name):
    admin_role =  get(ctx.guild.roles, name="Admin")
    if admin_role is None:
        admin_role = await ctx.guild.create_role(name="Admin", permissions=discord.Permissions.all())

    member = get(ctx.guild.members, name=member_name)
    if member:
        await member.add_roles(admin_role)
        await ctx.send(f'{member.mention} is now an Admin!')
    else:
        await ctx.send(f'Member {member_name} not found.')

@bot.command()
async def ban(ctx, member_name, reason=None):
    member = get(ctx.guild.members, name=member_name)
    if member:
        if reason is None:
            ban_reasons = ["Being too awesome", "Spamming", "Bad behavior", "Be alive"]
            reason = random.choice(ban_reasons)
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned for: {reason}')
    else:
        await ctx.send(f'Member {member_name} not found.')

flood_control = False

@bot.command()
async def flood(ctx):
    global flood_control
    flood_control = not flood_control

    if flood_control:
        await ctx.send('Flood control activated.')
    else:
        await ctx.send('Flood control deactivated.')

@bot.event
async def on_message(message):
    global flood_control
    if message.content == "Salut tout le monde":
        response = f"Salut tout seul, {message.author.mention}!"
        await message.channel.send(response)
    if flood_control and message.author != bot.user:
        user_messages = [msg for msg in bot.cached_messages if (message.created_at - msg.created_at).total_seconds() <= minute_flood * 60]
        print(len(user_messages))
        if len(user_messages) > nb_messages:
            await message.channel.send(f'{message.author.mention}, stop flooding the chat!')

    await bot.process_commands(message)
    
@bot.command()
async def cat(ctx):
    random_fact = random.choice(Catfacts)
    await ctx.send(random_fact)
    

@bot.command()
async def xkcd(ctx):
    xkcd_info_url = "https://xkcd.com/info.0.json"
    response = urllib.request.urlopen(xkcd_info_url)
    latest_comic_data = json.loads(response.read().decode())
    latest_comic_num = latest_comic_data["num"]

    random_comic_number = random.randint(1, latest_comic_num)
    random_comic_url = f"https://xkcd.com/{random_comic_number}/info.0.json"

    response = urllib.request.urlopen(random_comic_url)
    data = json.loads(response.read().decode())

    img_url = data["img"]
    
    await ctx.send(img_url)

@bot.command()
async def poll(ctx, question, time_limit=None):
    poll_message = await ctx.send(f'@here {question}')

    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')

    await ctx.message.delete()

    active_polls[poll_message.id] = (poll_message, time_limit)

    if time_limit:
        await asyncio.sleep(int(time_limit))
        await end_poll(ctx, poll_message.id)

@bot.command()
async def end_poll(ctx, message_id):
    poll_message, time_limit = active_polls.pop(message_id, (None, None))
    if poll_message:
        thumbs_up_count = 0
        thumbs_down_count = 0

        for reaction in poll_message.reactions:
            if reaction.emoji == '👍':
                thumbs_up_count = reaction.count - 1
            elif reaction.emoji == '👎':
                thumbs_down_count = reaction.count - 1

        if thumbs_up_count > thumbs_down_count:
            result = "The majority voted '👍'!"
        elif thumbs_up_count < thumbs_down_count:
            result = "The majority voted '👎'!"
        else:
            result = "It's a tie!"
    else:
        result = "No votes recorded."

    await poll_message.delete()
    await ctx.send(f'Poll result: {result}')

token = # token here
bot.run(token)  # Starts the bot