import discord
from discord.ext import commands, tasks
from discord.utils import get

from utils.VatsimData import VatsimData
VD = VatsimData()

from dotenv import load_dotenv
load_dotenv()

embed_colour = discord.Color.blue()

class atcCommands(commands.Cog):

  def __init__(self, client):
    self.client = client
  
  @commands.command(name="online", aliases=['enligne', 'Online', 'Enligne'])
  async def online_atc(self, ctx):
    data = VD.fetchATC()
    if len(data) > 0:
      embed = discord.Embed(color=embed_colour)
      embed.set_author(name="Online ATC")
      for d in data:
        embed.add_field(name=f"**{d['callsign']}**", value=f"**Nom / Name:** {d['name']}\n**Grade / Rating:** {d['rating']}\n**Depuis / Since:** {d['since']}", inline=False)
    else:
      embed = discord.Embed(color=embed_colour)
      embed.set_author(name="Online ATC")
      embed.add_field(name=f"**Pas d'ATC / No ATC**", value=f"Aucun contrôleur n'est en ligne en France\n\nNo ATC was found online in France", inline=False)
    await ctx.send(embed=embed)



def setup(client):
    client.add_cog(atcCommands(client))
