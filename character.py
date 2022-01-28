import json
import discord
from db import get_database
import time
import datetime

"""
  {
    "_id":str(ctx.author.id),
      "Progress":{
        "level":1,
        "XP":0,
      },
      "Stat":{
        "Attack":int(item_stat("Wooden Sword")),
        "Defence":int(item_stat("Leather Armor")),
        "Healt":100,
        "Max Healt":100
      },
      "Equipment":{
        "Weapon":"Wooden Sword",
        "Armor":"Leather Armor"
      },
    "Money":{
      "Gold":0
        },
    "Last Hunt":None,
    "Last Duel":None,
  }
"""

item_list = json.load(open("items.json"))

def create(ctx):
  db = get_database()
  users = db["samurai_rpg"]["users"]

  if users.count_documents({"_id":str(ctx.author.id)},limit = 1) != 0:
    return profile(ctx)
  else:
    new_user = {
    "_id":str(ctx.author.id),
      "level":1,
      "XP":0,
      "Attack":5,
      "Defence":5,
      "Healt":100,
      "Max Healt":100,
      "Weapon":None,
      "Armor":None,
      "Gold":0,
      "Last Hunt":None,
      "Last Duel":None,
      "Duel Joins":0,
      "Duel Wins":0
  }
    add_user = users.insert_one(new_user)


def item_stat(item_name,items = item_list):
  return items[item_name]["meta"]["stat"]

def profile(ctx):
  
  db = get_database()
  users= db["samurai_rpg"]["users"]
  user = users.find_one({"_id":str(ctx.author.id)})

  embed_profile =  discord.Embed(title=ctx.author.name +"'s profile" , color=0xFFFF00)
  embed_profile.set_thumbnail(url=ctx.author.avatar_url)

  embed_profile.add_field(name="PROGRESS", value = "**Level**: " + str(user["level"]) + "\n **XP**:" +str(user["XP"]) , inline=False)
  embed_profile.add_field(name="STAT", value = "**Attack**: " + str(user["Attack"]) + "\n **Defence**:" +str(user["Defence"]) + "\n **HP**:" + str(user["Healt"]), inline=False)

  embed_profile.add_field(name = "EQUIPMENT",value = "**Weapon**: " + str(user["Weapon"]) + "\n **Armor**:" +str(user["Armor"]), inline=True )
  embed_profile.add_field(name = "MONEY",value = "**Gold**: " + str(user["Gold"]), inline=True )
  
  if user["Duel Joins"] != 0:
    percent = user["Duel Wins"]/user["Duel Joins"]*100
  else:
    percent = 0
  duel_text = "**Duel Join:** {} \n **Duel Wins:** {} \n **Win Rate:** {}%".format(user["Duel Joins"],user["Duel Wins"],percent)
  embed_profile.add_field(name = "DUEL", value = duel_text, inline=False)

  return ctx.channel.send(embed=embed_profile)

class level_system:

  def check_level(ctx):
    user = get_database()["samurai_rpg"]["users"].find_one({"_id":str(ctx.author.id)})
    return user
  
def heal(ctx):
  db = get_database()["samurai_rpg"]["users"]
  user_max_healt = db.find_one({"_id":str(ctx.author.id)})["Max Healt"]
  heal = db.update_one({"_id":str(ctx.author.id)},{"$set":{"Healt":user_max_healt}})
  text = "HEAL"
  return text

def cooldown(ctx):
  db = get_database()["samurai_rpg"]["users"]
  user = db.find_one({"_id":str(ctx.author.id)})
  text = cooldown_text(user)
  embed_cd = discord.Embed(title = discord.Embed.Empty,color = 0x2f5696)
  embed_cd.set_footer(text = "{}'s cooldowns".format(ctx.author.name), icon_url = ctx.author.avatar_url)
  embed_cd.add_field(name=discord.Embed.Empty,value=text)
  return ctx.channel.send(embed=embed_cd)

def cooldown_text(user):
  now = datetime.datetime.now()
  hunt = user["Last Hunt"]
  duel = user["Last Duel"]
  
  if hunt != None:
    date_hunt = datetime.datetime.fromtimestamp(hunt)
    cd_hunt = time_text(now,date_hunt,5)
  else:
    cd_hunt = "Ready"
  
  if duel != None:
    date_duel = datetime.datetime.fromtimestamp(duel)
    cd_duel = time_text(now,date_duel,120)
  else:
    cd_duel = "Ready"

  text = "**Hunt**:{} \n **Duel**: {}".format(cd_hunt,cd_duel)
  return text

def time_text(now,user_data,cd_time):
  diff = now - user_data
  if diff > datetime.timedelta(minutes=cd_time):
    text = "Ready"
  else:
    diff = user_data + datetime.timedelta(minutes = cd_time) - now 
    hour = cd_time//60- int(diff.total_seconds()//3600)
    minutes = int((diff.total_seconds()%3600) // 60)
    seconds = int(diff.total_seconds()%60)
    text = "{}H {}M {}S ".format(hour,minutes,seconds)
  
  return text