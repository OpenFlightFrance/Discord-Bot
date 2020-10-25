import discord
from discord.ext import commands, tasks
from discord.utils import get

import time
import os
import mysql.connector
import requests
import json

from utils.VatsimData import VatsimData as VD

from dotenv import load_dotenv
load_dotenv()
OwnerID = int(os.getenv('OWNER_ID'))

class backgroundTasks(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.db_host = os.getenv('db_host')
    self.db_username = os.getenv('db_username')
    self.db_password = os.getenv('db_password')
    self.db_name = os.getenv('db_database_name')

    self.options = {
      'usersync': self.userSync,
      'username': self.usernameEditor,
      'activeatc': self.getVatsimControllers,
      'coord': self.update_coordchannels,
    }

    self.options_verbose = {
      'usersync': "Updates User Roles",
      'username': 'Updates User Nicknames',
      'activeatc': 'Updates cache of Active French ATC',
      'coord': 'Updates and maintains ATC coordination channels',
    }

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

    self.active_coordination = os.getenv('active_coordination').split(',')

    with open("utils/Airports.json", "r") as airports_file:
      self.airports = json.load(airports_file)

    self.guild_id = os.getenv('guild_id')
  
  @commands.Cog.listener()
  async def on_ready(self):
    for a in self.options:
      try:
        self.options[a].start()
      except Exception as e:
        pass
  
  def __error_embed_maker(self, task_name, error_log):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    current_date = time.strftime("%d/%m/%Y", t)
    embed = discord.Embed(title="Task failed", description=f"Task '{task_name}' failed at {current_time} {current_date}", color=0x272c88)
    embed.add_field(name=f"**Error log**", value=f"{error_log}", inline=True)
    return embed
              
  @tasks.loop(seconds=int(os.getenv('usersync_timer')))
  async def userSync(self):
    task_name = "User Role Sync"
    try:
      conn = mysql.connector.connect(
        host=str(self.db_host),
        user=str(self.db_username),
        password=str(self.db_password),
        database=str(self.db_name),
      )
      c = conn.cursor()

      query = "SELECT * FROM discord_data"
      c.execute(query)
      discord_data = c.fetchall()

      query = "SELECT * FROM users"
      c.execute(query)
      user_data = c.fetchall()

      query = "SELECT * FROM mentors"
      c.execute(query)
      all_atc_mentors = c.fetchall()
      atc_mentors_ids = [];
      for m in all_atc_mentors:
        atc_mentors_ids.append(m[0])
      
      query = "SELECT * FROM staff"
      c.execute(query)
      all_staff = c.fetchall()
      all_staff_ids = [];
      exec_staff_ids = [];
      for s in all_staff:
        all_staff_ids.append(s[0])
        if int(s[7]) == 1:
          exec_staff_ids.append(s[0])
      
      query = "SELECT * FROM atc_students"
      c.execute(query)
      all_students = c.fetchall()
      all_students_ids = [];
      for s in all_students:
        if s[3] == 1:
          all_students_ids.append(int(s[0]))

      guild = self.client.get_guild(int(self.guild_id))
      users = guild.members

      atc_rank_roles = {
        "2": get(guild.roles, id=int(os.getenv('r_s1'))),
        "3": get(guild.roles, id=int(os.getenv('r_s2'))),
        "4": get(guild.roles, id=int(os.getenv('r_s3'))),
        "5": get(guild.roles, id=int(os.getenv('r_c1'))),
        "7": get(guild.roles, id=int(os.getenv('r_c3'))),
        "8": get(guild.roles, id=int(os.getenv('r_i1'))),
        "10": get(guild.roles, id=int(os.getenv('r_i3'))),
      }

      atc_role = get(guild.roles, id=int(os.getenv('r_atc')))
      atc_student_role = get(guild.roles, id=int(os.getenv('r_stuatc')))
      atc_visiting_role = get(guild.roles, id=int(os.getenv('r_visatc')))
      member_role = get(guild.roles, id=int(os.getenv('r_member')))
      guest_role = get(guild.roles, id=int(os.getenv('r_guest')))
      atc_mentor = get(guild.roles, id=int(os.getenv('r_mentoratc')))
      pilote_mentor = get(guild.roles, id=int(os.getenv('r_mentorpilot')))

      staff_role = get(guild.roles, id=int(os.getenv('r_staff')))
      staff_exec_role = get(guild.roles, id=int(os.getenv('r_staff_exec')))
      bot_role = get(guild.roles, id=int(os.getenv('r_bot')))

      bloqued_role_obj = get(guild.roles, id=int(os.getenv('r_blocked')))

      member_list = []
      for d in discord_data:
        member_list.append(int(d[2]))
        for u in user_data:
          if u[0] == d[1]:
            for us in users:
              if not bot_role in us.roles:
                if us.id == int(d[2]):
                  if not bloqued_role_obj in us.roles:
                    # Assign member role and remove guest role
                    if guest_role in us.roles:
                      await us.remove_roles(guest_role)
                    if not member_role in us.roles:
                      await us.add_roles(member_role)

                    user_atc_rank = u[9]

                    # Adds or removes the ATC Student role when student is below C1 rank with an active mentoring
                    if int(u[0]) in all_students_ids:
                      if not atc_student_role in us.roles:
                          await us.add_roles(atc_student_role)
                    else:
                      if atc_student_role in us.roles:
                        await us.remove_roles(atc_student_role)
                    # Take care of ATC roles, remove unneeded and add needed
                    if user_atc_rank in atc_rank_roles:
                      if int(u[7]) == 0:
                        if atc_role in us.roles:
                          await us.remove_roles(atc_role)
                      if int(u[7]) == 1:
                        if not atc_role in us.roles:
                          await us.add_roles(atc_role)
                        
                      if int(u[8]) == 0:
                        if atc_visiting_role in us.roles:
                          await us.remove_roles(atc_visiting_role)
                      if int(u[8]) == 1:
                        if not atc_visiting_role in us.roles:
                          await us.add_roles(atc_visiting_role)
                      
                      for ar in atc_rank_roles:
                        if ar == user_atc_rank and not atc_rank_roles[ar] in us.roles:
                          await us.add_roles(atc_rank_roles[ar])
                        if ar != user_atc_rank and atc_rank_roles[ar] in us.roles:
                          await us.remove_roles(atc_rank_roles[ar])
                    
                    else:
                      if atc_role in us.roles:
                        await us.remove_roles(atc_role)
                      
                      for ar in atc_rank_roles:
                        if ar == user_atc_rank and not atc_rank_roles[ar] in us.roles:
                          await us.add_roles(atc_rank_roles[ar])
                        if ar != user_atc_rank and atc_rank_roles[ar] in us.roles:
                          await us.remove_roles(atc_rank_roles[ar])
                    # END of ATC only roles
                    
                    # Add / remove atc mentor role
                    if u[0] in atc_mentors_ids:
                      if not atc_mentor in us.roles:
                        await us.add_roles(atc_mentor)
                    else:
                      if atc_mentor in us.roles:
                        await us.remove_roles(atc_mentor)

                    # Add / remove staff role
                    if u[0] in all_staff_ids:
                      if not staff_role in us.roles:
                        await us.add_roles(staff_role)
                    else:
                      if staff_role in us.roles:
                        await us.remove_roles(staff_role)
                    
                    # Add / remove staff exec role
                    if u[0] in exec_staff_ids:
                      if not staff_exec_role in us.roles:
                        await us.add_roles(staff_exec_role)
                    else:
                      if staff_exec_role in us.roles:
                        await us.remove_roles(staff_exec_role)

      for u in users:
        if not bot_role in u.roles:
          if not u.id in member_list and not u.id == int(os.getenv('bot_id')) and not bloqued_role_obj in u.roles:
            if not guest_role in u.roles:
              await u.add_roles(guest_role)
            if member_role in u.roles:
              await u.remove_roles(member_role)
            if staff_role in u.roles:
              await u.remove_roles(staff_role)
            if staff_exec_role in u.roles:
              await u.remove_roles(staff_exec_role)
            if atc_mentor in u.roles:
              await u.remove_roles(atc_mentor)
            for ar in atc_rank_roles:
              if atc_rank_roles[ar] in u.roles:
                await u.remove_roles(atc_rank_roles[ar])
            if atc_role in u.roles:
              await u.remove_roles(atc_role)
            if atc_student_role in u.roles:
              await u.remove_roles(atc_student_role)
            if atc_visiting_role in u.roles:
              await u.remove_roles(atc_visiting_role)
      
      for u in users:
        if not bot_role in u.roles:
          if bloqued_role_obj in u.roles:
            techdev_role_obj = get(guild.roles, id=int(os.getenv('r_techdev')))
            admin_role_obj = get(guild.roles, id=int(os.getenv('r_admin')))
            if guest_role in u.roles:
              await u.remove_roles(guest_role)
            if member_role in u.roles:
              await u.remove_roles(member_role)
            if staff_role in u.roles:
              await u.remove_roles(staff_role)
            if staff_exec_role in u.roles:
              await u.remove_roles(staff_exec_role)
            if atc_mentor in u.roles:
              await u.remove_roles(atc_mentor)
            for ar in atc_rank_roles:
              if atc_rank_roles[ar] in u.roles:
                await u.remove_roles(atc_rank_roles[ar])
            if atc_role in u.roles:
              await u.remove_roles(atc_role)
            if atc_student_role in u.roles:
              await u.remove_roles(atc_student_role)
            if atc_visiting_role in u.roles:
              await u.remove_roles(atc_visiting_role)
            if techdev_role_obj in u.roles:
              await u.remove_roles(techdev_role_obj)
            if admin_role_obj in u.roles:
              await u.remove_roles(admin_role_obj)
      
      c.close()
      print(f"Done with Roles")
    except Exception as e:
      log_channel = self.client.get_channel(int(os.getenv('c_log_channel')))
      owner_ping = self.client.get_user(int(os.getenv('OWNER_ID')))
      embed_log = self.__error_embed_maker(task_name, e)
      print(f"{task_name} failed. Error: {e}")
      await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
      self.userSync.cancel()
  
  @tasks.loop(seconds=int(os.getenv('usersync_timer')))
  async def usernameEditor(self):
    task_name = "Username Editor"
    try:
      vatsim_url = "http://cluster.data.vatsim.net/vatsim-data.json"
      vatsim_data = requests.get(vatsim_url).text
      vatsim_data = json.loads(vatsim_data)['clients']

      v_data = {}
      for v in vatsim_data:
        if not v['callsign'][5:] == "ATIS":
          v_data[v['cid']] = v['callsign']

      conn = mysql.connector.connect(
        host=str(self.db_host),
        user=str(self.db_username),
        password=str(self.db_password),
        database=str(self.db_name),
      )
      c = conn.cursor()

      query = "SELECT * FROM discord_data"
      c.execute(query)
      discord_data = c.fetchall()

      query = "SELECT * FROM users"
      c.execute(query)
      user_data = c.fetchall()

      guild = self.client.get_guild(int(self.guild_id))
      bot_role = get(guild.roles, id=int(os.getenv('r_bot')))
      users = guild.members

      member_list = [];
      for d in discord_data:
        member_list.append(int(d[2]))
        for u in user_data:
          if u[0] == d[1]:
            for us in users:
              if us.id == int(d[2]):
                if not u[2] == None:
                  us_cid = str(u[1])
                  us_fname = u[2].capitalize()
                  us_lname = u[3].capitalize()
                  us_atcrank = u[10]
                else:
                  us_cid = str(u[1])
                  us_fname = str(u[1])
                  us_lname = "(inconnu)"
                  us_atcrank = u[10]

                if us_cid in v_data:
                  toset_uname = f"{us_fname} {us_lname[:1]}. - [{v_data[us_cid]}] {us_cid}"
                  if len(toset_uname) > 32:
                    toset_uname = f"{us_fname} {us_lname[:1]}. [{v_data[us_cid]}]"
                    if len(toset_uname) > 32:
                      toset_uname = f"{us_fname} [{v_data[us_cid]}]"
                      if len(toset_uname) > 32:
                        toset_uname = f"{us_fname}"
                
                else:
                  toset_uname = f"{us_fname} {us_lname[:1]}.  - {us_cid}"
                  if len(toset_uname) > 32:
                    toset_uname = f"{us_fname} {us_lname[:1]}."
                    if len(toset_uname) > 32:
                      toset_uname = f"{us_fname}"
                
                # edit user's display name / nickname
                try:
                  if not us.display_name == toset_uname:
                    await us.edit(nick=toset_uname)
                except Exception as e:
                  pass
      
      for u in users:
        if not bot_role in u.roles:
          if not u.id in member_list and not u.id == int(os.getenv('bot_id')):
            template = f"[Not Verified] - {u.name}"
            if len(template) > 32:
              template = f"{template[:31]}."
            
            # edit user's display name if they are unverified
            try:
              if not u.display_name == template:
                await u.edit(nick=template)
            except Exception as e:
              pass
          
      
      c.close()
      print("Done with Usernames")
    except Exception as e:
      log_channel = self.client.get_channel(int(os.getenv('c_log_channel')))
      owner_ping = self.client.get_user(int(os.getenv('OWNER_ID')))
      embed_log = self.__error_embed_maker(task_name, e)
      print(f"{task_name} failed. Error: {e}")
      await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
      self.usernameEditor.cancel()

  @tasks.loop(seconds=int(os.getenv('vatsimupdate_timer')))
  async def getVatsimControllers(self):
    task_name = "VATSIM Data"
    try:
      VD().updateActiveData()
      print("Done with Vatsim parsing")
    except Exception as e:
      log_channel = self.client.get_channel(int(os.getenv('c_log_channel')))
      owner_ping = self.client.get_user(int(os.getenv('OWNER_ID')))
      embed_log = self.__error_embed_maker(task_name, e)
      print(f"{task_name} failed. Error: {e}")
      await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
      self.getVatsimControllers.cancel()
  
  @tasks.loop(seconds=int(os.getenv('coordchannel_timer')))
  async def update_coordchannels(self):
    task_name = "Coord Channels"
    try:
      data = VD().fetchATC()
      required_channels = []
      for d in data:
        pos_type = d['callsign'][-3:]
        pos_icao = d['callsign'][:4]
        if pos_type in self.channel_types and pos_icao in self.active_coordination:
          channel_name = f"{pos_icao} {self.channel_types[pos_type]}"
          if not channel_name in required_channels:
            required_channels.append(channel_name)
        elif pos_type == "CTR":
          channel_name = f"{pos_icao} {self.channel_types[pos_type]}"
          if not channel_name in required_channels:
            required_channels.append(channel_name)
        else:
          fir_name = self.airports[pos_icao]
          channel_name = f"{fir_name}"
          if not channel_name in required_channels:
            required_channels.append(channel_name)
      required_channels = sorted(required_channels)
      
      guild = self.client.get_guild(int(self.guild_id))
      overwrites = {}
      coord_category = self.client.get_channel(int(self.coordcategory))
      existing_channels = []
      for c in coord_category.channels:
        existing_channels.append(c.name)
      for c in required_channels:
        if not c in existing_channels: # creates the channel if it does not exist yet
          await guild.create_voice_channel(c, overwrites=overwrites, category=coord_category)
        if c in existing_channels:
          existing_channels.remove(c)
      for c in existing_channels:
        if not c in required_channels:
          c_id = discord.utils.get(guild.channels, name=c).id
          if not "briefing" in c.lower():
            channel_todel = guild.get_channel(c_id)
            c_todel_members = channel_todel.members
            if len(c_todel_members) > 0:
              coord_lobby = guild.get_channel(int(os.getenv('c_coord_lobby')))
              for m in c_todel_members:
                await m.move_to(coord_lobby)
            await channel_todel.delete()
    except Exception as e:
      log_channel = self.client.get_channel(int(os.getenv('c_log_channel')))
      owner_ping = self.client.get_user(int(os.getenv('OWNER_ID')))
      embed_log = self.__error_embed_maker(task_name, e)
      print(f"{task_name} failed. Error: {e}")
      await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
      self.getVatsimControllers.cancel()
  
  # Background Task management commands
  @commands.command(name="start", aliases=['START', 'Start'])
  async def start(self, ctx, args):
    if ctx.author.id == OwnerID:
      args = args.split(" ")[0]
      if not args in self.options:
          await ctx.send(f"Option unknown. Choose one of the following: {', '.join(self.options)}")
      else:
          if args in self.options:
            try:
              self.options[args].start()
              await ctx.send(f"Starting task: {args}")
            except Exception as e:
              await ctx.send(f"Starting task {args} failed.\nError: {e}")
    else:
      await ctx.send(f"**Error:** you are not the owner of this bot")
    

  @commands.command(name="stop", aliases=['STOP', 'Stop'])
  async def stop(self, ctx, args):
    if ctx.author.id == OwnerID:
      args = args.split(" ")[0]
      if not args in self.options:
          await ctx.send(f"Option unknown. Choose one of the following: {', '.join(self.options)}")
      else:
          if args in self.options:
            try:
              self.options[args].cancel()
              await ctx.send(f"Stopping task: {args}")
            except Exception as e:
              await ctx.send(f"Stopping task {args} failed.\nError: {e}")
    else:
      await ctx.send(f"**Error:** you are not the owner of this bot")
    

  @commands.command(name="reboot", aliases=['REBOOT', 'Reboot'])
  async def reboot(self, ctx, args):
    if ctx.author.id == OwnerID:
      args = args.split(" ")[0]
      if not args in self.options:
          await ctx.send(f"Option unknown. Choose one of the following: {', '.join(self.options)}")
      else:
          if args in self.options:
            try:
              self.options[args].restart()
              await ctx.send(f"Rebooting task: {args}")
            except Exception as e:
              await ctx.send(f"Rebooting task {args} failed.\nError: {e}")
    else:
      await ctx.send(f"**Error:** you are not the owner of this bot")
    


  @commands.command()
  async def status(self, ctx):
    embed = discord.Embed(title="French vACC Bot", description=f"Current status of tasks", color=0x272c88)
    for t in self.options:
      st = self.options[t].get_task().done()
      if st:
          t_st = "**Stopped**"
      elif not st: 
          t_st = "*Running*"
      else:
          t_st = "***Unknown***"
      embed.add_field(name=f"**{t}**", value=f"Name: {t}\nDescription: {self.options_verbose[t]}\nStatus: {t_st}", inline=True)
    await ctx.send(embed=embed)

def setup(client):
  client.add_cog(backgroundTasks(client))
