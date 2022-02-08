import json
import discord
from db import get_database
import time
import datetime
import combat


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
        "Health":100,
        "Max Health":100
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

shop_list = json.load(open("data/shop.json"))
levels = json.load(open("data/levels.json"))

def create(ctx):
  db = get_database()
  users = db["samurai_rpg"]["users"]

  if users.count_documents({"_id":str(ctx.author.id)},limit = 1) != 0:
    return profile(ctx)
  else:
    new_user = {
    "_id":str(ctx.author.id),
      "name":ctx.author.name,
      "level":1,
      "total_xp":0,
      "XP":0,
      "Attack":5,
      "Defence":5,
      "Health":100,
      "Max Health":100,
      "Weapon":None,
      "Armor":None,
      "Gold":0,
      "Last Hunt":None,
      "Last Duel":None,
      "Last Meditate":None,
      "Duel Joins":0,
      "Duel Wins":0,
      "Monthly Duel":0,
      "Weekly Duel":0,
      "Inventory":{
        "Basic Health Potion":1
      }
  }
    add_user = users.insert_one(new_user)
    return profile(ctx)

def profile(ctx):
  
  db = get_database()
  users= db["samurai_rpg"]["users"]
  user = users.find_one({"_id":str(ctx.author.id)})

  embed_profile =  discord.Embed(title=ctx.author.name +"'s profile" , color=0xFFFF00)
  embed_profile.set_thumbnail(url=ctx.author.avatar_url)

  embed_profile.add_field(name="PROGRESS", value = "**Level**: " + str(user["level"]) + "\n**XP**: " +str(int(user["XP"]))+ "/" + str(levels[str(user["level"]+1)]["total_xp"]-levels[str(user["level"])]["total_xp"]), inline=True)
  embed_profile.add_field(name="STAT", value = "**Attack**: " + str(user["Attack"]) + "\n**Defence**: " +str(user["Defence"]) + "\n**HP**: " + str(user["Health"]) + "/" + str(user["Max Health"]), inline=True)
  embed_profile.add_field(name="\u200b", value="\u200b", inline=False)
  embed_profile.add_field(name = "EQUIPMENT",value = "**Weapon**: " + str(user["Weapon"]) + "\n**Armor**:" +str(user["Armor"]), inline=True )
  embed_profile.add_field(name = "MONEY",value = "**Gold**: " + str(user["Gold"]), inline=True )
  
  if user["Duel Joins"] != 0:
    percent = int(user["Duel Wins"]/user["Duel Joins"]*100)
  else:
    percent = 0
  duel_text = "**Duel Join:** {} \n**Duel Wins:** {} \n**Win Rate:** {}%".format(user["Duel Joins"],user["Duel Wins"],percent)
  embed_profile.add_field(name = "DUEL", value = duel_text, inline=True)

  return ctx.channel.send(embed=embed_profile)
  
def drink(ctx,item,piece):
  if item == "bhp":
    item = "basichealthpotion"
  if item in ("basichealthpotion"):
    db = get_database()["samurai_rpg"]["users"]
    user = db.find_one({"_id":str(ctx.author.id)})
    inv = user["Inventory"]
    inv_piece=inv[shop_list[item]["name"]]
    user_health = user["Health"]
    user_max_health = user["Max Health"]
    health_potion = inv[shop_list[item]["name"]]
    if inv_piece >= piece:
      if health_potion > 0 and user_health != user_max_health and shop_list[item]["type"]=="potion":
        user_max_health = user["Max Health"]
        inv[shop_list[item]["name"]] -=1
        health = shop_list[item]["stat"]*piece+user_health if user_max_health > shop_list[item]["stat"]*piece+user_health else user_max_health
        heal = db.update({"_id":str(ctx.author.id)},{"$set":{
          "Health":health,
          "Inventory":inv
          }})
        text = f"{ctx.author.name}, you drank the elixir and recovered your soul.\nYou've restored {shop_list[item]['stat']} health, now your health is {health}"
        return text
      elif user_health == user_max_health:
        text = "Your health already full"
        return text
      else:
        text = "You need buy heal potion.\n`!buy [potion]`"
        return text
    else:
      text = f"You don't have enough potion. You need to **{piece-inv_piece}** more potion.\n`!buy [potion]`"
      return text
  else:
    text = "**Drink commands**\n`drink basic health potion`\n`drink [drink name]`"
    return text

def cooldown(ctx):
  db = get_database()["samurai_rpg"]["users"]
  user = db.find_one({"_id":str(ctx.author.id)})
  text = cooldown_text(user)
  embed_cd = discord.Embed(title = discord.Embed.Empty,color = 0x2f5696)
  embed_cd.set_author(name = "{}'s cooldowns".format(ctx.author.name), icon_url = ctx.author.avatar_url)
  embed_cd.add_field(name="Combat",value=text)
  return ctx.channel.send(embed=embed_cd)

def cooldown_text(user):
  now = datetime.datetime.now()
  hunt = user["Last Hunt"]
  duel = user["Last Duel"]
  meditate = user["Last Meditate"]
  
  if hunt != None:
    date_hunt = datetime.datetime.fromtimestamp(hunt)
    cd_hunt = time_text(now,date_hunt,0.5)
  else:
    cd_hunt = "Ready"
  
  if duel != None:
    date_duel = datetime.datetime.fromtimestamp(duel)
    cd_duel = time_text(now,date_duel,120)
  else:
    cd_duel = "Ready"
  
  if meditate!= None:
    date_meditate = datetime.datetime.fromtimestamp(meditate)
    cd_meditate = time_text(now,date_meditate,240)
  else:
    cd_meditate = "Ready"

  text = "**Train**: {} \n**Duel**: {}\n**Meditate**: {}".format(cd_hunt,cd_duel,cd_meditate)
  return text

def time_text(now,user_data,cd_time):
  diff = now - user_data
  if diff > datetime.timedelta(minutes = cd_time):
    text = "Ready"
  else:
    diff = user_data + datetime.timedelta(minutes = cd_time) - now 
    hour = int(diff.total_seconds()//3600)
    minutes = int((diff.total_seconds()%3600) // 60)
    seconds = int(diff.total_seconds()%60)
    text = "{}H {}M {}S ".format(hour,minutes,seconds)
  return text 

def gain_xp(player,xp):
  
  db = get_database()["samurai_rpg"]["users"]
  user = db.find_one({"_id":player})

  lvl = user["level"]
  attack = user["Attack"]
  defence = user["Defence"]
  total_xp = user["total_xp"] + xp
  user_xp = user["XP"] + xp
  max_health = user["Max Health"]

  level_next = levels[str(lvl+1)]["total_xp"] if lvl < 100 else False
  count = 0
  
  if level_next != False: 
    while total_xp > level_next and 100 > lvl:
      user_xp = total_xp - levels[str(lvl)]["total_xp"]
      attack += 5
      defence += 5
      max_health +=15
      lvl += 1
      count +=1
      user_xp = total_xp - levels[str(lvl)]["total_xp"]
      level_next = levels[str(lvl+1)]["total_xp"]
    
    update_player = db.update(
        {"_id":player},{"$set":{
        "level":lvl,
        "total_xp":total_xp,
        "XP":user_xp,
        "Attack":attack,
        "Defence":defence,  
        "Max Health":max_health
        }})
  
    if count == 0:
      return " "
    else:
      return f"\nYou gain **{count}** lvl, +{count*5} attack and  +{count*5} defence"
  else:
    return " "

def meditate(ctx):
  db = get_database()["samurai_rpg"]["users"]
  user = db.find_one({"_id":str(ctx.author.id)})
  health = user["Health"]
  max_health = user["Max Health"]
  player_last = user["Last Meditate"]
  meditate_ready = combat.time_control(player_last,240)

  if meditate_ready == True:
    if max_health != health:
      heal = db.update({"_id":str(ctx.author.id)},{"$set":{
      "Health":max_health,
      "Last Meditate":time.time()
      }})
      text = f"{ctx.author.name}, you meditated and recovered your soul.\nNow your health is {max_health}"
      return text
    
    else:
      text = "Your health already full"
      return text


  else:
    text = "You have to wait " + meditate_ready
    return text

def leaderboard(ctx,value):
  
  db = get_database()["samurai_rpg"]["users"]
  count = 0

  if value == "top":
    text_leaderboard = "**Top 10 Leaderboard**\n```"
    for user in db.find().sort("total_xp",-1):
      count +=1
      if count <= 10:
        text_leaderboard+=f"{count}. {user['name']} - {user['level']} level\n"
  elif value == "weekly":
    text_leaderboard = "**Weekly Duel Leaderboard**\n```"
    for user in db.find().sort("Weekly Duel",-1):
      count +=1
      if count <= 10:
        text_leaderboard+=f"{count}. {user['name']} - {user['Weekly Duel']} Wins\n"
  elif value == "monthly":
    text_leaderboard = "**Monthly Duel Leaderboard**\n```"
    for user in db.find().sort("Monthly Duel",-1):
      count +=1
      if count <= 10:
        text_leaderboard+=f"{count}. {user['name']} - {user['Monthly Duel']} Wins\n"
  elif value == "duel":
    text_leaderboard = "**All Time Duel Leaderboard**\n```"
    for user in db.find().sort("Duel Wins",-1):
      count +=1
      if count <= 10:
        text_leaderboard+=f"{count}. {user['name']} - {user['Duel Wins']} Wins\n"
  text_leaderboard+="```"
  return ctx.channel.send(text_leaderboard)