import discord
import os
import character
import combat
import asyncio
from db import get_database
import json
import mercantile
import gamble

client = discord.Client()
shop_list = json.load(open("data/shop.json"))

@client.event
async def on_ready():
  print("We logged in as {0.user}"
  .format(client))

@client.event
async def on_message(ctx):

  if ctx.author == client.user:
    return

  if ctx.content.lower() == "help":
    embedVar = discord.Embed(title="Commands", color=0xFF0000)
    embedVar.add_field(name="Statistics commands", value="`profile`\n`cooldown`\n`inventory`", inline=True)
    embedVar.add_field(name="Combat commands", value="`train`\n`drink`\n`duel [@username]`\n`meditate`", inline=True)
    embedVar.add_field(name="Economy commands", value="`shop`\n`buy [item name]`\n`sell [weapon/armor]`", inline=True)
    embedVar.add_field(name="Gambling commands", value="`coinflip [head/tail]`", inline=True)
    embedVar.add_field(name="Leaderboard", value="`leaderboard top`\n`leaderboard duel`\n`leaderboard weekly`\n`leaderboard monthly`", inline=True)
    await ctx.channel.send(embed=embedVar)

  if ctx.content.lower() == "profile" :
    await character.create(ctx)
  
  if ctx.content.lower() == "train":
    await ctx.channel.send(combat.hunt(ctx))

  if ctx.content.lower().startswith("drink"):
    item = "".join([i for i in ctx.content.lower().replace("drink ","").replace(" ","") if not i.isdigit()])
    
    for word in ctx.content.split():
        if word.isdigit():
         piece = int(word)
        else:
          piece = 1  
    if ctx.content == "drink":
      await ctx.channel.send("**Drink commands**\n`drink basic health potion`\n`health [drink name]`")
    else:
      await ctx.channel.send(character.drink(ctx,item,piece))

  if ctx.content.lower().startswith("duel"):
    db = get_database()
    p1_name = ctx.author.name
    p1_id = str(ctx.author.id)
    p1_data = db["samurai_rpg"]["users"].find_one({"_id":p1_id})
    p1_lvl = p1_data["level"]

    p2_name = ctx.mentions[0].name
    p2_id = str(ctx.mentions[0].id)
    p2_data = db["samurai_rpg"]["users"].find_one({"_id":p2_id})
    p2_lvl = p2_data["level"]

    p1_cooldown = combat.time_control(p1_data["Last Duel"],120)
    p2_cooldown = combat.time_control(p2_data["Last Duel"],120)

    if p1_id == p2_id:
      text = "This is not fight club and you are not Tyler Durden."
      await ctx.channel.send(text)  

    elif p1_lvl + 1 == p2_lvl or p1_lvl - 1 == p2_lvl or p1_lvl == p2_lvl:  

      if p1_cooldown == True and p2_cooldown == True:  
        request_embed = discord.Embed(title=discord.Embed.Empty,color=0xD0BE86)
        request_embed.set_author(name = f"{p1_name}'s duel", icon_url=ctx.author.avatar_url)
        request_embed.add_field(name = f"**{p1_name}** challenged **{p2_name}**", value=f"**{p1_name}**: {p1_lvl} lvl \n**{p2_name}**: {p2_lvl} lvl", inline=False)
        request_embed.add_field(name = f"**{p2_name}** do you accept the duel? `yes/no`", value = "EMPTY FIELD",inline=False)
        await ctx.channel.send(embed=request_embed)
       
        if ctx.mentions[0].id != ctx.author.id:
          try:
            reply_message = await client.wait_for('message',check = lambda message: p2_id == str(message.author.id),timeout=15.0)
          except asyncio.TimeoutError:
              await ctx.channel.send("**{}** didn't reply".format(p2_name))
          else:
            if reply_message.content.lower() == "yes":
              duel_start, attack_list = combat.duel_start(ctx,p1_name,p2_name)
              await duel_start
              try:
                ret = await asyncio.gather(client.wait_for('message',check = lambda message: p1_id == str(message.author.id),timeout=15.0),
                client.wait_for('message',check = lambda message: p2_id == str(message.author.id),timeout=15.0),
                return_exceptions = True
                )  
              except asyncio.TimeoutError:
                  await ctx.channel.send("**{}** didn't reply".format(p2_name))
              ret = [r if not isinstance(r, Exception) else None for r in ret]
              p1_attack_type,p2_attack_type = ret
              if p1_attack_type.content in ("A","a","B","b","C","c") and p2_attack_type.content in ("A","a","B","b","C","c"):
                await combat.duel_result(ctx,attack_list,p1_attack_type.content,p1_name,p1_id,p1_data,p2_attack_type.content,p2_name,p2_id,p2_data)
      
      elif p1_cooldown == True and p2_cooldown != True:
        text = "{}'s ready but \n{}'s need: {} for duel.".format(p1_name,p2_name,p2_cooldown)
        await ctx.channel.send(text)

      elif p1_cooldown != True and p2_cooldown == True:
        text = "{}'s need: {} for duel.\n{}'s ready.".format(p1_name,p1_cooldown,p2_name)
        await ctx.channel.send(text)
        
      else:
        text = "{}'s need: {} for duel.\n{}'s need: {} for duel.".format(p1_name,p1_cooldown,p2_name,p2_cooldown)
        await ctx.channel.send(text)
    
    else:
      text = f"{p1_name} can't invate duel {p2_name}. \n**{p1_name}**: {p1_lvl} lvl\n**{p2_name}**: {p2_lvl} lvl"
      await ctx.channel.send(text)

  if ctx.content.lower() == "cooldown" :
    await character.cooldown(ctx)

  if ctx.content.lower() == "inventory":
    await mercantile.inventory(ctx)
  
  if ctx.content.lower().startswith("shop"):

    page_name,footer,text = mercantile.shop(ctx)

    if page_name != None:
      embed_shop = discord.Embed(title="Shop `!buy [item]`")
      embed_shop.add_field(name=page_name,value=text)
      embed_shop.set_footer(text = footer)
      await ctx.channel.send(embed=embed_shop)
    else:
       await ctx.channel.send("`shop`")

  if ctx.content.lower().startswith("buy"): 
    item = "".join([i for i in ctx.content.lower().replace("buy ","").replace(" ","") if not i.isdigit()])
    
    for word in ctx.content.split():
        if word.isdigit():
         piece = int(word)
        else:
          piece = 1  

    if ctx.content.lower() == "buy":
      await ctx.channel.send(f"<@{str(ctx.author.id)}>, that's true but you specify what you're getting. (`buy [item])` \nYou can check the shop for it. (`shop`)")

    elif item in shop_list.keys():
      await ctx.channel.send(mercantile.buy(ctx,item,piece))
    
    else:
      await ctx.channel.send(f"<@{str(ctx.author.id)}>, what are you trying to buy?. \nYou can look at the items on `shop` ")

  if ctx.content.lower().startswith("sell"):

    if ctx.content.lower() == "sell weapon":
      await ctx.channel.send(mercantile.sell(ctx,"Weapon"))
    elif ctx.content.lower() == "sell armor":
      await ctx.channel.send(mercantile.sell(ctx,"Armor"))
    else:
      await ctx.channel.send("**Sell commands**\n`sell armor`\n`sell weapon`")

  if ctx.content.lower().startswith("meditate"):
    await ctx.channel.send(character.meditate(ctx))

  if ctx.content.lower().startswith("leaderboard"):

    if ctx.content == "leaderboard top":
      await character.leaderboard(ctx,"top")
    elif ctx.content == "leaderboard weekly":
      await character.leaderboard(ctx,"weekly")
    elif ctx.content == "leaderboard monthly":
      await character.leaderboard(ctx,"monthly")
    elif ctx.content == "leaderboard duel":
      await character.leaderboard(ctx,"duel")
    else:
      await ctx.channel.send("**Leaderboard commands**\n`leaderboard top`\n`leaderboard weekly`\n`leaderboard monthly`\n`leaderboard duel`")
    
  if ctx.content.lower().startswith(("cf","coinflip")):
    await gamble.head_tail(ctx)
  
  if ctx.content.lower().startswith(("bj","blackjack")):
    
    for word in ctx.content.split():
        if word.isdigit():
         pot = int(word)
        else:
          pot = 1

    user = get_database()["samurai_rpg"]["users"].find_one({"_id":str(ctx.author.id)})
    user_gold = user["Gold"]
    if user_gold >= pot:
      start_game,p_hand,d_hand,p_sum = gamble.blackjack(ctx,pot)
      bj_token = True
      await start_game
      while p_sum < 21 and bj_token == True:
        try:
          reply_message = await client.wait_for('message',check = lambda message: user["_id"] == str(message.author.id),timeout=15.0)
        except asyncio.TimeoutError:
          await ctx.channel.send("**{}** didn't reply".format(user["name"]))
          bj_token = False
        else:
          if reply_message.content.lower() == "hit" and p_sum < 21:
            p_hand,p_sum = gamble.hit(p_hand)
            print(p_hand,p_sum)
          elif reply_message.content.lower() == "stand":
            print("else")
            bj_token = False
    else:
      await ctx.channel.send("`user_gold <= pot`")

client.run(os.getenv("DC_TOKEN"))
