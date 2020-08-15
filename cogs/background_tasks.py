import discord
from discord.ext import commands, tasks
from discord.utils import get

import time
import os
import mysql.connector

class backgroundTasks(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.db_host = os.getenv('db_host')
    self.db_username = os.getenv('db_username')
    self.db_password = os.getenv('db_password')
    self.db_name = os.getenv('db_database_name')

    self.options = {
      'usersync': self.userSync,
    }
  
  @commands.Cog.listener()
  async def on_ready(self):
    for a in self.options:
      try:
        self.options[a].start()
      except Exception as e:
        pass
              
  @tasks.loop(seconds=60)
  async def userSync(self):
    conn = mysql.connector.connect(
      host=str(self.db_host),
      user=str(self.db_username),
      password=str(self.db_password),
      database=str(self.db_name),
    )
    c = conn.cursor()

    query = "SELECT * FROM users"
    c.execute(query)
    result = c.fetchall()
    for row in result:
      print(f"User {row[2]} {row[3]}")
    
    c.close()

def setup(client):
    client.add_cog(backgroundTasks(client))