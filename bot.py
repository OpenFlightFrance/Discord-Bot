import discord
from discord.ext import commands, tasks
from discord.ext.commands import errors
from discord.utils import get

import os, time
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')

# Defining main variables
BOT_PREFIX = str(os.getenv('BOT_PREFIX'))
OwnerID = int(os.getenv('OWNER_ID'))

client = discord.Client()
client = commands.Bot(command_prefix=BOT_PREFIX)
client.remove_command("help")

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HEADER = '\033[95m'

@client.event
async def on_connect():
    print("Bot connected")

@client.event
async def on_ready():
    import datetime
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"French Skies"))
    print(f'Bot ready\nLogged on as {client.user}')
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    current_date = time.strftime("%d/%m/%Y", t)
    embed = discord.Embed(title="Bot Online", color=0x272c88)
    embed.add_field(name=f"**Bot came online at {current_time} {current_date}**", value=f"Reporting for ~~strike~~ **duty**, Sir!", inline=True)
    log_channel = client.get_channel(int(os.getenv('c_log_channel')))
    await log_channel.send(embed=embed)

def load_cogs():
    print(f"{bcolors.BOLD}{bcolors.HEADER}Loading extensions{bcolors.ENDC}")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not "__" in filename:
            client.load_extension(f"cogs.{filename[:-3]}")
            print(f"{bcolors.OKGREEN}Loaded cog:{bcolors.ENDC} {filename}")
        else:
            if not filename == "__pycache__":
                print(f"{bcolors.WARNING}Ignored cog:{bcolors.ENDC} {filename}")
    print(f"{bcolors.BOLD}{bcolors.OKBLUE}DONE.{bcolors.ENDC}")

@client.command()
async def load(ctx, cogname):
    if ctx.author.id == OwnerID:
        if f"{cogname}.py" in os.listdir("./cogs") and not "__" in cogname:
            try:
                client.load_extension(f"cogs.{cogname}")
                await ctx.send(f"**Loaded:** {cogname}")
                print(f"{bcolors.OKGREEN}Loaded cog:{bcolors.ENDC} {cogname}")
                return
            except commands.errors.ExtensionAlreadyLoaded:
                await ctx.send(f"**Error:** {cogname} is already loaded")
                return
        else:
            await ctx.send(f"**Error:** {cogname} does not exist")
    else:
        await ctx.send(f"**Error:** you are not the owner of this bot")

@client.command()
async def unload(ctx, cogname):
    if ctx.author.id == OwnerID:
        if f"{cogname}.py" in os.listdir("./cogs") and not "__" in cogname:
            try:
                client.unload_extension(f"cogs.{cogname}")
                await ctx.send(f"**Unloaded:** {cogname}")
                print(f"{bcolors.WARNING}Unloaded cog:{bcolors.ENDC} {cogname}")
                return
            except commands.errors.ExtensionNotLoaded:
                await ctx.send(f"**Error:** {cogname} is not yet loaded")
                return
        else:
            await ctx.send(f"**Error:** {cogname} does not exist")
    else:
        await ctx.send(f"**Error:** you are not the owner of this bot")

@client.command()
async def reload(ctx, cogname):
    if ctx.author.id == OwnerID:
        if f"{cogname}.py" in os.listdir("./cogs") and not "__" in cogname:
            try:
                client.unload_extension(f"cogs.{cogname}")
            except:
                pass
            try:
                client.load_extension(f"cogs.{cogname}")
            except:
                await ctx.send("Error occured loading the cog")
                return
            await ctx.send(f"**Reloaded:** {cogname}")
            print(f"{bcolors.OKGREEN}Reloaded cog:{bcolors.ENDC} {cogname}")
        else:
            await ctx.send(f"**Error:** {cogname} does not exist")
    else:
        await ctx.send(f"**Error:** you are not the owner of this bot")

@client.command()
async def listcogs(ctx):
    if ctx.author.id == OwnerID:
        cogs_list = []
        for cog in os.listdir("./cogs"):
            if not "__" in cog:
                cogs_list.append(cog[:-3])
        nl = "\n"
        await ctx.send(f"**Detected cogs are**:\n{nl.join(cogs_list)}")
    else:
        await ctx.send(f"**Error:** you are not the owner of this bot")


@client.command()
async def logout(ctx):
    if ctx.author.id == OwnerID:
        await client.logout()

load_cogs()
client.run(TOKEN)
