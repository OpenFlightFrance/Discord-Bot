import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
load_dotenv()
admin_role = int(os.getenv('r_admin'))

class adminCommands(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.admin_role = int(os.getenv('r_admin'))
  
  @commands.command()
  @commands.has_role(admin_role)
  async def clear(self, ctx, amount=5):
    amount = amount + 1
    await ctx.channel.purge(limit=amount)



def setup(client):
  client.add_cog(adminCommands(client))
