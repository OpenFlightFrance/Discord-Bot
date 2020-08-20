import discord
from discord.ext import commands
from discord.utils import get

import os, mysql.connector
from dotenv import load_dotenv
load_dotenv()
admin_role = int(os.getenv('r_admin'))
bloqued_role = int(os.getenv('r_blocked'))

class adminCommands(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.admin_role = int(os.getenv('r_admin'))

    self.db_host = os.getenv('db_host')
    self.db_username = os.getenv('db_username')
    self.db_password = os.getenv('db_password')
    self.db_name = os.getenv('db_database_name')
  
  @commands.command()
  @commands.has_role(admin_role)
  async def clear(self, ctx, amount=5):
    amount = amount + 1
    await ctx.channel.purge(limit=amount)
  
  @commands.command(name="block", aliases=['Block', 'bloquer', 'Bloquer'])
  @commands.has_role(admin_role)
  async def block(self, ctx, user : discord.Member = None):
    if user == None:
      await ctx.send("Vous n'avez pas spécifié un utilisateur à bloquer.")
      return
    
    guild = self.client.get_guild(int(os.getenv('guild_id')))
    
    bloqued_role_obj = get(guild.roles, id=int(os.getenv('r_blocked')))
    if bloqued_role_obj in user.roles:
      await ctx.send(f"{user.mention} est déjà bloqué. Pour le débloquer, utilisez `unblock` / `débloquer`")
      return
    
    conn = mysql.connector.connect(
      host=str(self.db_host),
      user=str(self.db_username),
      password=str(self.db_password),
      database=str(self.db_name),
    )
    c = conn.cursor()
    query = f"UPDATE `discord_data` SET `banned` = '1' WHERE `discord_data`.`discord_id` = {user.id}"
    c.execute(query)
    conn.commit()
    conn.close()
    
    await user.add_roles(bloqued_role_obj)
    await ctx.send(f"{user.mention} est maintenant bloqué.")
  
  @commands.command(name="unblock", aliases=['Unblock', 'débloquer', 'Débloquer'])
  @commands.has_role(admin_role)
  async def unblock(self, ctx, user : discord.Member = None):
    if user == None:
      await ctx.send("Vous n'avez pas spécifié un utilisateur à débloquer.")
      return
    
    guild = self.client.get_guild(int(os.getenv('guild_id')))
    
    bloqued_role_obj = get(guild.roles, id=int(os.getenv('r_blocked')))
    if not bloqued_role_obj in user.roles:
      await ctx.send(f"{user.mention} n'est pas bloqué.")
      return
    
    conn = mysql.connector.connect(
      host=str(self.db_host),
      user=str(self.db_username),
      password=str(self.db_password),
      database=str(self.db_name),
    )
    c = conn.cursor()
    query = f"UPDATE `discord_data` SET `banned` = '0' WHERE `discord_data`.`discord_id` = {user.id}"
    c.execute(query)
    conn.commit()
    conn.close()
    
    await user.remove_roles(bloqued_role_obj)
    await ctx.send(f"{user.mention} est maintenant débloqué.")
    




def setup(client):
  client.add_cog(adminCommands(client))
