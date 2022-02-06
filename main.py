import discord
import os
import character
import combat
import asyncio
from db import get_database
import json
import mercantile

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

  if ctx.content=="help":
    embedVar = discord.Embed(title="Commands", color=0xFF0000)
    embedVar.add_field(name="Statistics commands", value="`profile`, `cooldown`,`inventory`", inline=True)
    embedVar.add_field(name="Combat commands", value="`train`,`heal`, `duel`, `meditation`", inline=True)
    embedVar.add_field(name="Economy commands", value="`shop`, `buy`, `sell`", inline=True)
    embedVar.add_field(name="Gambling commands", value="Will be added with in future", inline=True)
    embedVar.add_field(name="Leaderboard", value="Will be added with in future", inline=True)
    await ctx.channel.send(embed=embedVar)

  if ctx.content == "profile" :
    await character.create(ctx)
  
  if ctx.content == "train":
    await ctx.channel.send(combat.hunt(ctx))

  if ctx.content.startswith("heal"):
    await ctx.channel.send(character.heal(ctx))

  if ctx.content.startswith("duel"):
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
            if reply_message.content == "yes":
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
        text = "{}'s need: {} for duel.\n{}'s ready.".format(p1_name,p1_data,p2_name)
        await ctx.channel.send(text)
        
      else:
        text = "{}'s need: {} for duel.\n{}'s need: {} for duel.".format(p1_name,p1_cooldown,p2_name,p2_cooldown)
        await ctx.channel.send(text)
    
    else:
      text = f"{p1_name} can't invate duel {p2_name}. \n**{p1_name}**: {p1_lvl} lvl\n**{p2_name}**: {p2_lvl} lvl"
      await ctx.channel.send(text)

  if ctx.content == "cooldown" :
    await character.cooldown(ctx)

  if ctx.content == "inventory":
    await mercantile.inventory(ctx)
  
  if ctx.content.startswith("shop"):

    page_name,footer,text = mercantile.shop(ctx)

    if page_name != None:
      embed_shop = discord.Embed(title="Shop `!buy [item]`")
      embed_shop.add_field(name=page_name,value=text)
      embed_shop.set_footer(text = footer)
      await ctx.channel.send(embed=embed_shop)
    else:
       await ctx.channel.send("`shop`")

  if ctx.content.startswith("buy"): 
    item = "".join([i for i in ctx.content.replace("buy ","").replace(" ","").lower() if not i.isdigit()])
    
    for word in ctx.content.split():
        if word.isdigit():
         piece = int(word)
        else:
          piece = 1  

    if ctx.content == "buy":
      await ctx.channel.send(f"<@{str(ctx.author.id)}>, that's true but you specify what you're getting. (`buy [item])` \nYou can check the shop for it. (`shop`)")

    elif item in shop_list.keys():
      await ctx.channel.send(mercantile.buy(ctx,item,piece))
    
    else:
      await ctx.channel.send(f"<@{str(ctx.author.id)}>, what are you trying to buy?. \nYou can look at the items on `shop` ")

  if ctx.content.startswith("sell"):

    if ctx.content == "sell weapon":
      await ctx.channel.send(mercantile.sell(ctx,"Weapon"))
    if ctx.content == "sell armor":
      await ctx.channel.send(mercantile.sell(ctx,"Armor"))

  if ctx.content.startswith("meditation"):
    await ctx.channel.send(character.meditation(ctx))

client.run("OTMzMzQyMDQ3NTQzMzg2MTEz.YegIhA.8rvMeXIPdjCrAjBIoCxWxAXJSfo")