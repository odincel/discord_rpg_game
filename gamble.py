import random

from matplotlib.pyplot import title
from db import get_database
import discord

deck = {
  "♦️":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "♣️":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "♥️":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "♠️":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"]
}
deck_shape = ("♦️","♣️","♥️","♠️")

def head_tail(ctx):
    db = get_database()["samurai_rpg"]["users"]
    user = db.find_one({"_id":str(ctx.author.id)})
    user_money=user["Gold"]

    if ctx.content.lower().startswith("cf"):
        user_text = "".join([i for i in ctx.content.lower().replace("cf ","").replace(" ","") if not i.isdigit()])
    else:
        user_text = "".join([i for i in ctx.content.lower().replace("coinflip ","").replace(" ","") if not i.isdigit()])
    
    for word in ctx.content.split():
        if word.isdigit():
         pot = int(word)
        else:
          pot = 1  

    if user_text in ("head","tail"):
        if user_money >= pot:
            coin_flip = random.choice(("head","tail"))
            if user_text==coin_flip:
                pot *=2
                user_money += pot
                title = "Win"
                text = f"You chose {user_text.upper()} and it came {coin_flip.upper()}. You won {pot} gold"
            else:
                user_money -= pot
                title="Lost"
                text = f"You chose {user_text.upper()} and it came {coin_flip.upper()}. You lost {pot} gold"
            update =db.update({"_id":str(ctx.author.id)},{"$set":{"Gold":user_money}})
            
            embed_coin = discord.Embed(title=discord.Embed.Empty,color = 0x3E8B75)
            embed_coin.set_author(name=ctx.author.name,icon_url=ctx.author.avatar_url)
            embed_coin.add_field(name=title,value=text)

            return ctx.channel.send(embed=embed_coin)
        else:
            text= f"**{ctx.author.name}** you can't afford it."
            return ctx.channel.send(text)
    else:
        text= "**Coin Flip command**\n`cf [head/tail]`"
        return ctx.channel.send(text)

def blackjack(ctx,pot):
    
    p_hand = {}
    d_hand = {}

    p_hand = deal(p_hand)
    d_hand = deal(d_hand)
    p_sum = sum_hand(p_hand)
    d_sum = sum_hand(d_hand)
    
    if d_hand[0]["num"] in ("J","Q","K"):
      d_1 = 10
    elif d_hand[0]["num"]=="A":
      d_1 = 11
    else:
        d_1=d_hand[0]["num"]


    embed = discord.Embed(title=discord.Embed.Empty,color=0x3E8B75)
    embed.set_author(name=ctx.author.name+"blackjack",icon_url=ctx.author.avatar_url)
    embed.add_field(name="Answer with `hit` to draw another card or stay to `pass`",value=f"Pot size: **{pot}** Gold",inline=False)
    embed.add_field(name=f"**{ctx.author.name} Hand**",value=f"`{p_hand[0]['num']}{p_hand[0]['shape']}` `{p_hand[1]['num']}{p_hand[1]['shape']}`\nTotal: {p_sum}",inline=True)
    embed.add_field(name=f"**Dealer Hand**", value=f"`{d_hand[0]['num']}{d_hand[0]['shape']}` `?`\nTotal: {d_1}",inline=True)

    return ctx.channel.send(embed=embed),p_hand,d_hand




def deal(hand):
  for i in range(2):
    shape = random.choice(deck_shape)
    card = deck[shape].pop()
    hand[i]={"shape":shape,"num":card}
  return hand

def sum_hand(hand):
  sum = 0
  for i in hand.keys():
    if hand[i]["num"] in ("J","Q","K"):
      num = 10
    elif hand[i]["num"]=="A":
      pass
    else:
      num = hand[i]["num"]  
    sum += num
  return sum