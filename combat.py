import json
import discord
import random
import time

from sklearn import ensemble
import character
from db import get_database


enemy_dict = json.load(open("enemy.json"))
level_dict = dict()
client = discord.Client()

for enemy in enemy_dict.keys():
  level_dict[enemy] = enemy_dict[enemy]["level"]

def hunt(ctx):
  db = get_database()
  user = db["samurai_rpg"]["users"].find_one({"_id":str(ctx.author.id)})
  player_attack = user["Attack"]
  player_defence = user["Defence"]
  player_healt = user["Healt"]

  enemy = get_enemy(str(ctx.author.id))
  enemy_attack = enemy_dict[enemy]["Attack"]
  enemy_defence = enemy_dict[enemy]["Defence"]
  enemy_healt = enemy_dict[enemy]["Healt"]
  
  turn = 0
  while player_healt > 0 and enemy_healt > 0:
    if (turn%2) == 0:
      #player turn
      hit = player_attack - enemy_defence
      if hit <= 0:
        text = "Draw"
        return text
      else:
        enemy_healt -= hit
        turn += 1
    else:
      #enemy turn
      hit = enemy_attack - player_defence
      if hit <= 0:
        turn += 1
        pass
      else:
        player_healt -= hit
        turn += 1

    if player_healt <= 0:
      text = "player death"
      update = db["samurai_rpg"]["users"].update_one({"_id":str(ctx.author.id)},{"$set":{"Healt":player_healt}})
      return text
  
    if enemy_healt <= 0:
      text = "**{}** killed a **{}** \n Earned {} coins and {} xp. \n {} HP is {}/{}".format(

        ctx.author.name,enemy.upper(),"**COIN**","**XP**",ctx.author.name,player_healt,user["Max Healt"]
        
        )
      update = db["samurai_rpg"]["users"].update_one({"_id":str(ctx.author.id)},{"$set":{"Healt":player_healt}})
      return text
  return ""

def get_enemy(player):
  user = get_database()["samurai_rpg"]["users"].find_one({"_id":player})
  enemys = dict((k, v) for k, v in level_dict.items() if v == user["level"]) 
  selected = random.choice(list(enemys.keys()))
  return selected

def duel(ctx):
  db = get_database()["samurai_rpg"]["users"]
  
  p1_name = ctx.author.name
  p1_id = str(ctx.author.id)
  p1_data = db.find_one({"_id":p1_id})
  p1_lvl = p1_data["level"]

  p2_name = ctx.mentions[0].name
  p2_id = str(ctx.mentions[0].id)
  p2_data = db.find_one({"_id":p2_id})
  p2_lvl = p2_data["level"]

  if p1_lvl + 1 == p2_lvl or p1_lvl - 1 == p2_lvl or p1_lvl == p2_lvl:  
    text = "{} invate duel to {}".format(p1_name,p2_name)
    return ctx.channel.send(text)
  
  else:
    text = "You can't invate duel {}.".format(p1_name,p2_name)
    return ctx.channel.send(text)

def duel_start(ctx,p1_name,p2_name):
  attack_list = random.sample(["attack","balance","defence"],3)
  text = "**{}**,**{}**, choose the attacking style: \n `A`: {} \n `B`: {} \n `C`: {} ".format(p1_name,p2_name,attack_list[0],attack_list[1],attack_list[2])
  embed_duel = discord.Embed(title = "**{}'s** duel".format(p1_name),color=0xFF0000)
  embed_duel.add_field(name = "-", value=text)
  return ctx.channel.send(embed = embed_duel),attack_list

def duel_result(ctx,attack_list,p1_type,p1_name,p1_id,p2_type,p2_name,p2_id):
  db = get_database()["samurai_rpg"]["users"]

  p1_att,p1_df,p2_att,p2_df = which_attack(attack_list,p1_type,p2_type)
  
  duel_time = time.time()

  p1_attack = db.find_one({"_id":p1_id})["Attack"] * p1_att
  p1_defence = db.find_one({"_id":p1_id})["Defence"] * p1_df
  p1_duel_wins = db.find_one({"_id":p1_id})["Duel Wins"]
  p1_duel_joins = db.find_one({"_id":p1_id})["Duel Joins"] + 1


  p2_attack = db.find_one({"_id":p2_id})["Attack"] * p2_att
  p2_defence = db.find_one({"_id":p2_id})["Defence"] * p2_df
  p2_duel_wins = db.find_one({"_id":p2_id})["Duel Wins"]
  p2_duel_joins = db.find_one({"_id":p2_id})["Duel Joins"] + 1 



  p1_dmg =  p1_attack - p2_defence 
  p2_dmg =  p2_attack - p1_defence 

  if p1_dmg < 0:
    p1_dmg = 0
    
  if p2_dmg < 0:
    p2_dmg = 0

  if p1_dmg > p2_dmg:
    winner = winner = "Winner: " + p1_name
    
    p1_update = db.update({"_id":p1_id},{"$set":{"Duel Joins":p1_duel_joins,
    "Duel Wins":p1_duel_wins+1,
    "Last Duel":duel_time}})

    p2_update = db.update({"_id":p2_id},{"$set":{"Duel Joins":p2_duel_joins,
    "Last Duel":duel_time}})


  if p2_dmg > p1_dmg:
    winner = "Winner: " + p2_name
    p2_update = db.update({"_id":p2_id},{"$set":{"Duel Joins":p2_duel_joins,
    "Duel Wins":p2_duel_wins+1,
    "Last Duel":duel_time}})

    p1_update = db.update({"_id":p1_id},{"$set":{"Duel Joins":p1_duel_joins,
    "Last Duel":duel_time}})

  else:
    winner = "Draw Duel"

  embed_result = discord.Embed(title = "{} VS {}".format(p1_name,p2_name))
  text = "{}'s damage: {} \n {}'s damage: {} \n  {} \n ".format(p1_name,p1_dmg,p2_name,p2_dmg,winner)
  embed_result.add_field(name = "-", value=text)
  return ctx.channel.send(embed = embed_result)

def which_attack(attack_list,p1,p2):
  attack_dict = {"attack":(1.2,0.8),"balance":(1,1),"defence":(0.8,1.2)}
  if p1 == "A" or p1 == "a":
    p1_attack = attack_dict[attack_list[0]][0]
    p1_defence = attack_dict[attack_list[0]][1]
  if p1 == "B" or p1 == "b":
    p1_attack = attack_dict[attack_list[1]][0]
    p1_defence = attack_dict[attack_list[1]][1]
  if p1 == "C" or p1 == "c":
    p1_attack = attack_dict[attack_list[2]][0]
    p1_defence = attack_dict[attack_list[2]][1]
  if p2 == "A" or p2 == "a":
    p2_attack = attack_dict[attack_list[0]][0]
    p2_defence = attack_dict[attack_list[0]][1]
  if p2 == "B" or p2 == "b":
    p2_attack = attack_dict[attack_list[1]][0]
    p2_defence = attack_dict[attack_list[1]][1]
  if p2 == "C" or p2 == "c":
    p2_attack = attack_dict[attack_list[2]][0]
    p2_defence = attack_dict[attack_list[2]][1]
  return p1_attack,p1_defence,p2_attack,p2_defence