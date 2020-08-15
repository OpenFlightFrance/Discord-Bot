import discord
from discord.ext import commands, tasks
from discord.ext.commands import errors
from discord.utils import get

import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')

client = discord.Client()
client = commands.Bot(command_prefix="!")
client.remove_command("help")


@client.event
async def on_ready():
    print("Logged on")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"Au chomage technique (je ne fais rien pour l'instant)"))


client.run(TOKEN)