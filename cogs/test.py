import discord, os
from discord.ext import commands, tasks
from discord.utils import get

from utils.VatsimData import VatsimData
VD = VatsimData()

from dotenv import load_dotenv
load_dotenv()

embed_colour = discord.Color.blue()

class testing(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.coordcategory = int(os.getenv('c_coordcategory'))
    self.channel_types = {
      'DEL': 'Visual Room',
      'GND': 'Visual Room',
      'TWR': 'Visual Room',
      'APP': 'Radar Room',
      'DEP': 'Radar Room',
      'CTR': 'Enroute',
      'FSS': 'Enroute',
    }
    self.guild_id = os.getenv('guild_id')
  
  @commands.command(name="ch")
  async def ch_command(self, ctx):
    pass
      



def setup(client):
    client.add_cog(testing(client))
