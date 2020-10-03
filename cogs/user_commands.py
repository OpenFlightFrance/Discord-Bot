import discord
from discord.ext import commands

import os, mysql.connector, json, requests
from dotenv import load_dotenv
load_dotenv()

embed_colour = discord.Color.blue()

class userCommands(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.db_host = os.getenv('db_host')
    self.db_username = os.getenv('db_username')
    self.db_password = os.getenv('db_password')
    self.db_name = os.getenv('db_database_name')
  
  @commands.command(name="userinfo", aliases=['user', 'utilisateur', 'Userinfo', 'User', 'Utilisateur'])
  async def userinfo(self, ctx, user : discord.Member = None):
    conn = mysql.connector.connect(
      host=str(self.db_host),
      user=str(self.db_username),
      password=str(self.db_password),
      database=str(self.db_name),
    )
    c = conn.cursor()

    if user == None:
      discord_id = ctx.author.id
      discord_obj = ctx.author
    else:
      discord_id = user.id
      discord_obj = user

    query = f"SELECT * FROM `discord_data` WHERE `discord_id` = {discord_id}"
    c.execute(query)
    user_id = c.fetchone()[1]
    print(user_id)
    query = f"SELECT * FROM `users` WHERE `id` = {user_id}"
    c.execute(query)
    user_data = c.fetchone()
    print(user_data)
    print(user_data[21])
    if user_data[21] == 1:
      embed = discord.Embed(color=embed_colour)
      embed.set_author(name=f"User information for {discord_obj.display_name}")
      embed.add_field(name="**Avis de Confidentialité / Privacy Notice**", value=f"*Cet utilisateur a choisi de cacher ses données personnelles*\n*This user has chosen to hide their personal details*", inline=False)
      embed.set_footer(text="Generated automatically from https://vatsim.fr/ website data")
      await ctx.send(embed=embed)
      return
    
    user_cid = user_data[1]
    vatsim_url_times = f"https://api.vatsim.net/api/ratings/{user_cid}/rating_times"
    vatsim_url_connections = f"https://api.vatsim.net/api/ratings/{user_cid}/connections"
    user_fname = user_data[2]
    user_lname = user_data[3]
    user_type = user_data[6]
    user_pilotrank = user_data[11]
    user_atcrank = user_data[9]
    user_region = f"{user_data[14]} - {user_data[15]}"
    user_division = f"{user_data[12]} - {user_data[13]}"
    user_subdiv = f"{user_data[16]} - {user_data[17]}"

    hours_data = requests.get(vatsim_url_times).text
    hours_data = json.loads(hours_data)
    user_hours_atc = hours_data['atc']
    user_hours_pilot = hours_data['pilot']

    conn_data = requests.get(vatsim_url_connections).text
    conn_data = json.loads(conn_data)['results']
    if not len(conn_data) == 0:
      foundConn = False
      for co in conn_data:
        if not co['callsign'][5:] == "ATIS" and foundConn == False:
          foundConn = True
          connd = f"**Last Connection:** {co['callsign']}"
      if foundConn == False:
        connd = ""
    else:
      connd = ""

    embed = discord.Embed(color=embed_colour)
    embed.set_author(name=f"User information for {discord_obj.display_name}")
    embed.add_field(name="**PROFILE**", value=f"""**Name:** {user_fname} {user_lname} - {discord_obj.mention}
    **Account type:** {user_type}
    **Vatsim ID and ratings:** {user_cid} | {user_atcrank} | P{user_pilotrank}
    **Division info:** {user_division} | {user_region} | {user_subdiv}""", inline=False)
    embed.add_field(name="**STATISTICS**", value=f"""**ATC hours:** {user_hours_atc}h
    **Pilots hours:** {user_hours_pilot}h
    {connd}""", inline=False)
    embed.add_field(name="**LINKS**", value=f"[Vatsim statistics page](https://stats.vatsim.net/search_id.php?id={user_cid})", inline=False)
    embed.set_footer(text="Generated automatically from https://vatsim.fr/ website data")
    await ctx.send(embed=embed)

    conn.close()
  
  @commands.command(name="help", aliases=['aide', 'Help', 'Aide'])
  async def help_command(self, ctx):
    await ctx.send("Hah! Help is on the way, but not yet finished. Come back later")
    await ctx.send("Hah! La commande d'aide n'est pas encore toute prête... Soyez patient!")

  
def setup(client):
  client.add_cog(userCommands(client))