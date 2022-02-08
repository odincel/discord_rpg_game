import datetime
import json
import discord
import random
import time
import character
from db import get_database


enemy_dict = json.load(open("data/enemy.json"))
level_dict = dict()
client = discord.Client()

for enemy in enemy_dict.keys():
  level_dict[enemy] = enemy_dict[enemy]["level"]

def hunt(ctx):
  db = get_database()
  user = db["samurai_rpg"]["users"].find_one({"_id":str(ctx.author.id)})
  player_lvl = user["level"]
  player_attack = user["Attack"]
  player_defence = user["Defence"]
  player_health = user["Health"]
  player_last = user["Last Hunt"]

  enemy = get_enemy(player_lvl)
  enemy_health,enemy_attack, enemy_defence = enemy_stat(player_lvl)
  xp,gold = xp_gold(player_lvl)
  hunt_ready = time_control(player_last,1)

  if player_health == 0:
    text = f"{ctx.content.name}, you have 0 health right now, it might help to heal\n `heal [potion]`"
    return text
  
  elif hunt_ready == True:
    turn = 0
    while player_health > 0 and enemy_health > 0:
      if (turn%2) == 0:
        #player turn
        hit = player_attack - enemy_defence
        if hit <= 0:
          text = f"**{ctx.author.name}** running away because you're not strong enough to kill **{enemy}**.\nYou should buy better equipment."
          return text
        else:
          enemy_health -= hit
          turn += 1
      else:
        #enemy turn
        hit = enemy_attack - player_defence
        if hit <= 0:
          turn += 1
          pass
        else:
          player_health -= hit
          turn += 1

      if player_health <= 0:
        text = f"**{enemy}** brutally killed **{ctx.author.name}**"
        update = db["samurai_rpg"]["users"].update({"_id":str(ctx.author.id)},{"$set":{
          "Health":0,
          "Last Hunt":time.time()
        }})
        return text
    
      if enemy_health <= 0:
        text = "**{}** killed a **{}** \nEarned **{}** coins and **{}** xp. \n{} HP is {}/{}".format(

          ctx.author.name,enemy.upper(),gold,xp,ctx.author.name,player_health,user["Max Health"]
          
          )
        update = db["samurai_rpg"]["users"].update({"_id":str(ctx.author.id)},{"$set":{
          "Health":player_health,
          "Last Hunt":time.time(),
          "Gold":int(user["Gold"]+gold)
          }})
        text += character.gain_xp(str(ctx.author.id),xp)
        return text
  
        
  else:
    text = "You have to wait "+hunt_ready
    return text
       
def get_enemy(player):
  player = player // 5 + 1
  enemys = dict((k, v) for k, v in level_dict.items() if v == player) 
  selected = random.choice(list(enemys.keys()))
  return selected

def duel_start(ctx,p1_name,p2_name):
  attack_list = random.sample(["Attack","Defence","Keen Mind","The Tower","Backstab","Roughlike"],3)
  text = f" `A`: {attack_list[0]} \n`B`: {attack_list[1]} \n`C`: {attack_list[2]} "
  embed_duel = discord.Embed(title = "**{}'s** duel".format(p1_name),color=0xFF0000)
  embed_duel.set_author(name=p1_name,icon_url=ctx.author.avatar_url)
  embed_duel.add_field(name = f"**{p1_name}** and **{p2_name}** what style of attack will you choose?", value=text)
  return ctx.channel.send(embed = embed_duel),attack_list

def duel_result(ctx,attack_list,p1_type,p1_name,p1_id,p1_data,p2_type,p2_name,p2_id,p2_data):
  db = get_database()["samurai_rpg"]["users"]

  p1_att,p1_df,p2_att,p2_df = which_attack(attack_list,p1_type,p2_type)
  
  duel_time = time.time()

  p1_attack = p1_data["Attack"] * 2 * p1_att
  p1_defence = p1_data["Defence"] * p1_df
  p1_duel_wins = p1_data["Duel Wins"]
  p1_duel_weekly = p1_data["Weekly Duel"]
  p1_duel_monthly = p1_data["Monthly Duel"]
  p1_duel_joins = p1_data["Duel Joins"] + 1
  p1_lvl = p1_data["level"]

  p2_attack = p2_data["Attack"] * 2 * p2_att
  p2_defence = p2_data["Defence"] * p2_df
  p2_duel_wins = p2_data["Duel Wins"]
  p2_duel_weekly = p2_data["Weekly Duel"]
  p2_duel_monthly = p2_data["Monthly Duel"]
  p2_duel_joins = p2_data["Duel Joins"] + 1 
  p2_lvl = p2_data["level"]

  p1_dmg =  round(p1_attack - p2_defence)
  p2_dmg =  round(p2_attack - p1_defence)

  if p1_dmg < 0:
    p1_dmg = 0
    
  if p2_dmg < 0:
    p2_dmg = 0

  if p1_dmg > p2_dmg:
    winner = "Winner: " + p1_name
    xp,gold = xp_gold(p2_lvl)
    xp_update= character.gain_xp(p1_id,xp*2)

    p1_update = db.update({"_id":p1_id},{"$set":{"Duel Joins":p1_duel_joins,
    "Duel Wins":p1_duel_wins+1,
    "Monthly Duel":p1_duel_monthly+1,
    "Weekly Duel":p1_duel_weekly+1,
    "Last Duel":duel_time,
    "Gold":p2_data["Gold"]+int(gold*2)
    }})

    p2_update = db.update({"_id":p2_id},{"$set":{"Duel Joins":p2_duel_joins,
    "Last Duel":duel_time}})
    text = f"**{winner}** \nEarn: **{gold*2}** GOLD **{xp*2}** XP \n"+xp_update


  elif p2_dmg > p1_dmg:
    winner = "Winner: " + p2_name
    xp,gold = xp_gold(p1_lvl)
    xp_update = character.gain_xp(p2_id,xp*2)

    p2_update = db.update({"_id":p2_id},{"$set":{"Duel Joins":p2_duel_joins,
    "Duel Wins":p2_duel_wins+1,
    "Monthly Duel":p2_duel_monthly+1,
    "Weekly Duel":p2_duel_weekly+1,
    "Last Duel":duel_time,
    "Gold":p2_data["Gold"]+int(gold*2)
    }})

    p1_update = db.update({"_id":p1_id},{"$set":{"Duel Joins":p1_duel_joins,
    "Last Duel":duel_time}})
    text = f"**{winner}** \nEarn: **{gold*2}** GOLD **{xp*2}** XP \n"+xp_update
  
  else:
    text = "Draw Duel"

  embed_result = discord.Embed(title = f"{p1_name} vs {p2_name} result")
  embed_result.add_field(name = f"**{p1_name}**'s damage: {p1_dmg} \n**{p2_name}**'s damage: {p2_dmg}", value=text)
  return ctx.channel.send(embed = embed_result)

def which_attack(attack_list,p1,p2):
  attack_dict = {"Attack":(1.5,1,20),"Defence":(1,1.5,20),"Keen Mind":(2,1,95),"The Tower":(1,2,90),"Backstab":(1,6,1,40),"Roughlike":(1.8,1,60)}
  if p1 in ("a","A"):
    p1_style = attack_dict[attack_list[0]]
  elif p1 in ("b","B"):
    p1_style = attack_dict[attack_list[1]]
  elif p1 in ("c","C"):
    p1_style = attack_dict[attack_list[2]]
  if p2 in ("a","A"):
    p2_style = attack_dict[attack_list[0]]
  elif p2 in ("b","B"):
    p2_style = attack_dict[attack_list[1]]
  elif p2 in ("c","C"):
    p2_style = attack_dict[attack_list[2]]

  if p1_style[2] <= random.randint(1,100):
    p1_attack = p1_style[0]
    p1_defence = p1_style[1]
  else:
    p1_attack = 0.9
    p1_defence = 0.9

  if p2_style[2] <= random.randint(1,100):
    p2_attack = p2_style[0]
    p2_defence = p2_style[1]
  else:
    p2_attack = 0.9
    p2_defence = 0.9

  return p1_attack,p1_defence,p2_attack,p2_defence

def time_control(time,cd_time):
  combat = False
  if time == None:
    combat = True
    return combat
  else:
    now = datetime.datetime.now()
    player = datetime.datetime.fromtimestamp(time)
    diff = now - player

    if diff > datetime.timedelta(seconds=cd_time):
      combat = True
      return combat
    else:
      cooldown = player + datetime.timedelta(minutes = cd_time) - now
      hour = int(cooldown.total_seconds()//3600)
      minutes = int((cooldown.total_seconds()%3600) // 60)
      seconds = int(cooldown.total_seconds()%60)
      text = "{} hour {} minute {} second".format(hour,minutes,seconds)
      return text

def xp_gold(lvl):
  
  xp_base = 10
  xp_multiple = 1.05

  gold_base = 8
  gold_multiple = 1.1

  xp = int(xp_base*xp_multiple**lvl*random.uniform(0.85,1.15))
  gold = int(gold_base*gold_multiple**lvl*random.uniform(0.85,1.15))

  return xp,gold

def enemy_stat(lvl):
  hp = 25+(lvl-1)*25
  attack = 1 + round(round((lvl//5) + round(lvl//10)*5 + round(lvl//25)*10 + (lvl)*5)*random.uniform(0.75,1.15))
  defence = round(round((lvl//5) + round(lvl//10)*5 + round(lvl//25)*10 + (lvl)*5)*random.uniform(0.85,1))-1 
  return hp,attack,defence