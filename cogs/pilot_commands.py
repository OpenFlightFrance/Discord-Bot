import discord
from discord.ext import commands, tasks
from discord.utils import get

import os, requests, json
from dotenv import load_dotenv
load_dotenv()

METAR_TOKEN = os.getenv('METAR_TOKEN')

embed_colour = discord.Color.blue()

class pilotCommands(commands.Cog):

  def __init__(self, client):
    self.client = client
  
  @commands.command(name="metar", aliases=['Metar'])
  async def metar_command(self, ctx, icao = None):
    if icao:
      icao = icao.upper()

      embed = self.metar_maker(METAR_TOKEN, icao)

      await ctx.send(embed=embed)
    else:
      await ctx.send(f"Please give me an ICAO to fetch.")
  
  def metar_maker(self, metarKey, icao):
    hdr = {'X-API-Key': metarKey}
    req = requests.get(f'https://api.checkwx.com/metar/{icao}/decoded?pretty=1', headers=hdr)

    metarJSON = json.loads(req.text)
    if not metarJSON['results'] == 0:
      station_name = metarJSON['data'][0]['station']['name']
      wind_dir = metarJSON['data'][0]['wind']['degrees']
      wind_kts = metarJSON['data'][0]['wind']['speed_kts']
      wind_data = f"{wind_dir} degrees \n{wind_kts} knots"
      temp_cel = metarJSON['data'][0]['temperature']['celsius']
      dew_cel = metarJSON['data'][0]['dewpoint']['celsius']
      bar_qnh = metarJSON['data'][0]['barometer']['hpa']
      bar_hg = metarJSON['data'][0]['barometer']['hg']
      vis_m = metarJSON['data'][0]['visibility']['meters']
      fl_cat = metarJSON['data'][0]['flight_category']
      full_metar = metarJSON['data'][0]['raw_text']

      embed = discord.Embed(color=0x272c88)
      embed.set_author(name=f"Metar for {icao} - {station_name}", url="https://vatsim.fr")
      embed.add_field(name="**WINDS**", value=wind_data, inline=True)
      embed.add_field(name="**TEMPERATURE**", value=f"{temp_cel} Celsius", inline=True)
      embed.add_field(name="**DEW POINT**", value=f"{dew_cel} Celsius", inline=True)
      embed.add_field(name="**BAROMETER**", value=f"{bar_qnh} hPa \n{bar_hg} inHg", inline=True)
      embed.add_field(name="**VISIBILITY**", value=f"{vis_m} meters", inline=True)
      embed.add_field(name="**FLIGHT CATEGORY**", value=f"{fl_cat} able", inline=True)

      cloudsData = ""
      i = 0
      for i in metarJSON['data'][0]['clouds']:
        if i["code"] == "CAVOK":
          cloudsData = f"{i['code']} and {i['text']}"
        elif i["code"] == "CLR":
          cloudsData = f"{i['code']} and {i['text']}"
        else:
          cloudsData = f"{i['text']} at {i['base_feet_agl']} feet \n{cloudsData}"

      embed.add_field(name="**CLOUDS**", value=cloudsData, inline=True)

      condData = "No further conditions"
      i = 0
      for i in metarJSON['data'][0]['conditions']:
        condData = f"{i['code']} | {i['text']} \n{condData}"

      embed.add_field(name="**CONDITIONS**", value=condData, inline=True)
      embed.add_field(name="**METAR**", value=full_metar, inline=False)
      embed.set_footer(text="Metar Generator by French vACC and CheckWX")
    else:
      embed = discord.Embed(color=0x272c88)
      embed.set_author(name=f"Metar for {icao}", url="https://vatsim.fr")
      embed.add_field(name="**ERROR**", value="No METAR found", inline=True)

    return embed
  
  # Metar Raw data command, outputs raw metar
  @commands.command(name="metarraw", aliases=['Metarraw'], pass_context=True)
  async def metarraw(self, ctx, icao):
    if icao:
      icao = icao.upper()

      hdr = {'X-API-Key': METAR_TOKEN}
      req = requests.get(f'https://api.checkwx.com/metar/{icao}', headers=hdr)
      metarJSON = json.loads(req.text)

          
      results = metarJSON['results']
      if not results == 0:
        metardata = metarJSON['data']
        for m in metardata:
          embed = discord.Embed(color=0x272c88)
          embed.set_author(name=f"Metar for {icao}", url="https://vatsim.fr")
          embed.add_field(name=f"{results} result(s) found", value=m, inline=True)
          embed.set_footer(text="Metar Generator by French vACC and CheckWX")
                  
      else:
        embed = discord.Embed(color=0x272c88)
        embed.set_author(name=f"Metar for {icao}", url="https://vatsim.fr")
        embed.add_field(name="**ERROR**", value="No METAR found", inline=True)
      await ctx.send(embed=embed)
    else:
      await ctx.send(f"Please give me an ICAO to fetch.")



def setup(client):
  client.add_cog(pilotCommands(client))
