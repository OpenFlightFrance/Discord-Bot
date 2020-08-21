import discord
from discord.ext import commands
from discord.ext.commands import errors

import time, os
from dotenv import load_dotenv
load_dotenv()
bot_prefix = str(os.getenv('BOT_PREFIX'))

class bcolors:
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  HEADER = '\033[95m'

class eventsCommands(commands.Cog):
  
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    current_date = time.strftime("%d/%m/%Y", t)

    if isinstance(error, errors.MissingRole) or isinstance(error, errors.MissingPermissions):
      await ctx.send("You do not have the permission to use this command.")
      to_log = f"[{current_date} {current_time}] - User {ctx.author.id} attempted to invoke {ctx.message.content} without authorisation."
    
    elif isinstance(error, errors.MissingRequiredArgument):
      await ctx.send(f"Command missing arguments. If in doubt, use `{bot_prefix}help`")
      to_log = f"[{current_date} {current_time}] - User {ctx.author.id} attempted to invoke {ctx.message.content} with missing requirements."
    
    elif isinstance(error, errors.CommandNotFound):
      print(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} User {ctx.author.id} invoked unknown command: '{ctx.message.content}'")
      to_log = f"[{current_date} {current_time}] - User {ctx.author.id} attempted to invoke unknown command '{ctx.message.content}'."
    
    else:
      print(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} {error}")
      to_log = f"[{current_date} {current_time}] - User {ctx.author.id} attempted to invoke {ctx.message.content}. Provoked error: {error}"
      #await ctx.send(f"An error occured. Please report the error message below to a tech team member\n\n**Error message:** {error}")

def setup(client):
  client.add_cog(eventsCommands(client))