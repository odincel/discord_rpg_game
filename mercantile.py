import json
import discord
from db import get_database

shop_list = json.load(open("data/shop.json"))
levels = json.load(open("data/levels.json"))

def inventory(ctx):
  db = get_database()["samurai_rpg"]["users"]
  inv = db.find_one({"_id":str(ctx.author.id)})["Inventory"]
  text = ""

  if len(list(inv.keys())) > 0:
    for key, value in inv.items():
      new_line = "{}: {} \n".format(key,value)
      text += new_line
  else:
    text = "Your inventory empty."

  embed_inv = discord.Embed(title=discord.Embed.Empty)
  embed_inv.set_author(name=f"{ctx.author.name}'s inventory", icon_url=ctx.author.avatar_url)
  embed_inv.add_field(name="Items",value=text)
  return ctx.channel.send(embed=embed_inv)

def buy(ctx,item,piece):
  db = get_database()["samurai_rpg"]["users"]
  user = db.find_one({"_id":str(ctx.author.id)})
  player_gold = user["Gold"]

  item_type = shop_list[item]["type"]
  item_cost = shop_list[item]["cost"]*piece

  if player_gold >= item_cost and user["level"] >= shop_list[item]["level"]:

    inv = user["Inventory"]

    if item_type not in ("Weapon","Armor"):
      if shop_list[item]["name"] in inv:
        inv[shop_list[item]["name"]] += piece
      else:
        inv[shop_list[item]["name"]] = piece
      
      gold = player_gold-item_cost
      
      inv[shop_list[item]["name"]] += piece
      update_player = db.update({"_id":str(ctx.author.id)},{"$set":{
      "Gold":gold,
      "Inventory":inv
      }})
      if piece == 1:
        text = f"You bought a {shop_list[item]['name']} for {item_cost} gold, your current gold is {gold}."
      else:
        text = f"You bought {piece} pieces of {shop_list[item]['name']} for {item_cost} gold, your current gold is {gold}."
      return text     

    if item_type == "Weapon":

      if user["Weapon"] == None:
        
        gold = player_gold-item_cost
        player_attack = user["Attack"] + shop_list[item]["stat"]

        update_player = db.update({"_id":str(ctx.author.id)},{"$set":{
      "Gold":gold,
      "Weapon":shop_list[item]["name"],
      "Attack":player_attack
      }})
        text = f"You bought a {shop_list[item]['name']} for {item_cost} gold, your current gold is {gold}."
        return text

      else:
        text = f"{ctx.author.name} now you have a {user['Weapon']}.\nYou need sell your current weapon.\n`sell weapon` to make the sale weapon"
        return text

    if item_type == "Armor":

      if user["Armor"] == None:
        
        gold = player_gold-item_cost
        player_attack = user["Defence"] + shop_list[item]["stat"]

        update_player = db.update({"_id":str(ctx.author.id)},{"$set":{
      "Gold":gold,
      "Armor":shop_list[item]["name"],
      "Defence":player_attack
      }})
        text = f"You bought a {shop_list[item]['name']} for {item_cost} gold, your current gold is {gold}"
        return text

      else:
        text =f"{ctx.author.name} now you have a {user['Armor']}.\nYou need sell your current weapon.\n`sell armor` to make the sale armor"
        return text

  elif item_cost > player_gold:
    text = f"Your gold not enough for {shop_list[item]['name']}"
    return text
  
  else:
    text = f"Your lvl not enough for {shop_list[item]['name']}"
    return text

def sell(ctx,item):
  db = get_database()["samurai_rpg"]["users"]
  user = db.find_one({"_id":str(ctx.author.id)})
  player_item = user[item]
  if player_item != None:
    item_name = player_item.lower().replace(" ","")
    item_cost = shop_list[item_name]["cost"]*0.8
    item_stat = shop_list[item_name]["stat"]

    gold = user["Gold"] + item_cost
    stat = "Defence" if item == "Armor" else "Attack"
    player_stat = user[stat] - item_stat
    update_player = db.update(
      {"_id":str(ctx.author.id)},{"$set":{
      "Gold":gold,
      item:None,
      stat:player_stat
      }})

    text= f"**{ctx.author.name}** sell *{player_item}* \n Gain: **{int(item_cost)}** gold. \n **{ctx.author.name}** have {int(gold)} gold"
    return text
  else:
    text = f"You don't have any {item} at the moment."
    return text

def shop(ctx):
  item_name = ctx.content.replace("shop ","").lower() 
  if ctx.content == "shop":
    page_name = "Basic Items"
    footer = "!shop [potion] [tanto] [armor]"
    text = ""
    for key in shop_list.keys():
      if shop_list[key]["shop page"] == "basic":
        text += "`{}`: {} - **{} gold** \n".format(shop_list[key]["name"],shop_list[key]["info"],shop_list[key]["cost"])

  elif item_name in ("tanto","wakizashi","katana","nagamaki","omiyari","armor","metal armor"):
    page_name = f"{item_name.title()} Shop"
    
    if item_name in ("tanto","wakizashi"):
      footer = "!shop [tanto] [wakizashi]" 
    
    elif item_name in ("armor","metalarmor"):
      footer = "!shop [armor] [metal armor]"

    else:
      footer = "!shop [potion] [tanto] [armor]"
    
    text = ""
    for key in shop_list.keys():
      if shop_list[key]["shop page"] == item_name:
        text += "`{}`: {} - **{} gold** \n".format(shop_list[key]["name"],shop_list[key]["info"],shop_list[key]["cost"])
    
  return page_name,footer,text
