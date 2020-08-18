import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
load_dotenv()

class memberJoinLeave(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.welcome_channel = int(os.getenv('c_welcome_channel'))
    self.rules_channel = int(os.getenv('c_rules_channel'))
    self.join_channel = int(os.getenv('c_join_channel'))

  @commands.Cog.listener()
  async def on_member_join(self, member):
    channel = self.client.get_channel(self.welcome_channel)
    rules_c = self.client.get_channel(self.rules_channel)
    join_c = self.client.get_channel(self.join_channel)

    await channel.send(
      f"""Bienvenue {member.mention}!
      N'oublie pas d'aller jeter un coup d'oeil aux règles dans la chaine {rules_c.mention}.
      Ensuite, **pour accéder au serveur, suis les instructions dans la chaine {join_c.mention}!**

      Welcome {member.mention}!
      Don't forget to read the rules in the {rules_c.mention} channel.
      Then, **to access the server, follow the instructions in the {join_c.mention} channel!**"""
    )
  
  @commands.Cog.listener()
  async def on_member_remove(self, member):
    channel = self.client.get_channel(self.welcome_channel)
    await channel.send(f'{member.mention} a quitté le serveur.')

def setup(client):
    client.add_cog(memberJoinLeave(client))
