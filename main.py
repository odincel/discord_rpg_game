import discord
import os

from sympy import prime
import character
import combat
import asyncio

client = discord.Client()

@client.event
async def on_ready():
  print("We logged in as {0.user}"
  .format(client))

@client.event
async def on_message(ctx):

  if ctx.author == client.user:
    return

  if ctx  .content.startswith("$help"):
    embedVar = discord.Embed(title="Commands", color=0xFF0000)
    embedVar.add_field(name="Statistics commands", value="profile", inline=False)
    embedVar.add_field(name="Field2", value="hi2", inline=False)
    await ctx.channel.send(embed=embedVar)

  if ctx.content.startswith("$profile"):
    await character.create(ctx)
  
  if ctx.content.startswith("$train"):
    await ctx.channel.send(combat.hunt(ctx))

  if ctx.content.startswith("$heal"):
    await ctx.channel.send(character.heal(ctx))

  if ctx.content.startswith("$duel"):
    p1_name = ctx.author.name
    p1_id = str(ctx.author.id)
  
    p2_name = ctx.mentions[0].name
    p2_id = str(ctx.mentions[0].id)
    await combat.duel(ctx)

    if ctx.mentions[0] != ctx.author.id:
      try:
        reply_message = await client.wait_for('message',check = lambda message: p2_id == str(message.author.id),timeout=10.0)
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
          if (p1_attack_type.content ==  "A" or p1_attack_type.content ==  "a" or p1_attack_type.content == "B" or p1_attack_type.content ==  "b" or p1_attack_type.content ==  "C" or p1_attack_type.content ==  "c") and (p2_attack_type.content == "A" or p2_attack_type.content == "a" or p2_attack_type.content == "B" or p2_attack_type.content == "b" or p2_attack_type.content == "C" or p2_attack_type.content == "c"):
            await combat.duel_result(ctx,attack_list,p1_attack_type.content,p1_name,p1_id,p2_attack_type.content,p2_name,p2_id)
    elif ctx.mentions[0] == ctx.author.id:
      text = "This is not fight club and your not Tyler Durden"
    return ctx.channel.send(text)

  if ctx.content.startswith("$cooldown"):
    await character.cooldown(ctx)

client.run(os.environ("DC_TOKEN"))