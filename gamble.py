import random
from db import get_database
import discord
import json

deck_shape = ("bj-spade","bj-diamond","bj-hearth","bj-hearth")
emoji = json.load(open("data/emoji.json"))

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
  user_gold = get_database()["samurai_rpg"]["users"].update({"_id":str(ctx.author.id)},{"$set":{
  "Gold":get_database()["samurai_rpg"]["users"].find_one({"_id":str(ctx.author.id)})["Gold"]-pot}})
  
  global deck
  deck = {
  "bj-spade":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "bj-diamond":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "bj-hearth":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "bj-hearth":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"]
  } 

  for key in deck.keys():
    random.shuffle(deck[key])

  p_hand = {}
  d_hand = {}

  p_hand = deal(p_hand)
  d_hand = deal(d_hand)
  p_sum = sum_hand(p_hand)
  d_sum = sum_hand(d_hand)
  
  embed = bj_message(ctx,pot,p_hand,p_sum,d_hand)
  return ctx.channel.send(embed=embed),p_hand,d_hand,p_sum

def deal(hand):
  for i in range(2):
    shape = random.choice(deck_shape)
    card = deck[shape].pop()
    hand[i]={"shape":shape,"num":card}
  return hand

def sum_hand(hand):
  hand_list = []
  for i in hand.keys():
    if hand[i]["num"] in ("J","Q","K"):
     hand_list.append(10)
    elif hand[i]["num"]=="A":
      hand_list.append(11)
    else:
      hand_list.append(hand[i]["num"])
  hand_sum = sum(hand_list)
  while hand_sum > 21 and 11 in hand_list:
      hand_list.pop(hand_list.index(11))
      hand_list.append(1)
  hand_sum = sum(hand_list)
  return hand_sum

def hit(hand):
  shape = random.choice(deck_shape)
  card = deck[shape].pop()
  hand[len(hand.keys())]={"shape":shape,"num":card}
  hand_sum = sum_hand(hand)
  return hand,hand_sum

def bj_message(ctx,pot,p_hand,p_sum,d_hand):
  text  = ""
  for card in p_hand.keys():
    text += "**"+str(p_hand[card]["num"])+"**"+ " " +str(emoji[p_hand[card]['shape']]) + " "

  embed = discord.Embed(title=discord.Embed.Empty,color=0x3E8B75)
  embed.set_author(name=ctx.author.name+"blackjack",icon_url=ctx.author.avatar_url)
  embed.add_field(name="Answer with `hit` to draw another card or stay to `stand`",value=f"Pot size: **{pot}** Gold",inline=False)
  embed.add_field(name= f"{ctx.author.name}" ,value = text + f"\n Total: `{p_sum}`" ,inline=True)
  embed.add_field(name=f"**Dealer Hand**", value=f"**{d_hand[0]['num']}** {emoji[d_hand[0]['shape']]} `?`\nTotal: `?`",inline=True)
  return embed

def stand(ctx,pot,p_hand,p_sum,d_hand):

  d_sum = sum_hand(d_hand)

  while d_sum < 17:
    d_hand,d_sum = hit(d_hand) 
  if d_sum == p_sum:
    state = "Tie"
    embed_value = f" Dealer's hand and your hand are equal."
  elif d_sum == 21:
    state = "You Lose"
    embed_value = f"Dealer got a blackjack.\nYou lose **{pot}** gold"
  elif d_sum > 21:
    state = "You Won"
    embed_value = f"Dealer busts.\nYou won **{pot}** gold"
  elif d_sum < p_sum:
    state = "You Won"
    embed_value = f"Congratulations. Your score is higher than the dealer.\nYou won **{pot}** gold"
  elif d_sum > p_sum:
    state = "You Lose"
    embed_value = f" Your score isn't higher than the dealer.\nYou lose **{pot}** gold"

  if state == "You Won":
    update = get_database()["samurai_rpg"]["users"].update({"_id":str(ctx.author.id)},{"$set":{
  "Gold":get_database()["samurai_rpg"]["users"].find_one({"_id":str(ctx.author.id)})["Gold"]+(pot*2)}})
  elif state =="Tie":
    update = get_database()["samurai_rpg"]["users"].update({"_id":str(ctx.author.id)},{"$set":{
  "Gold":get_database()["samurai_rpg"]["users"].find_one({"_id":str(ctx.author.id)})["Gold"]+pot}})

  text_player = ""
  text_dealer = ""
  for card in p_hand.keys():
    text_player += "**"+str(p_hand[card]["num"])+ "** " + " " + str(emoji[p_hand[card]['shape']]) + " "
  for card in d_hand.keys():
    text_dealer += "**"+str(d_hand[card]["num"])+ "** "+ " " +str(emoji[d_hand[card]['shape']]) + " "

  embed = discord.Embed(title=discord.Embed.Empty,color=0x3E8B75)
  embed.set_author(name=ctx.author.name+"blackjack",icon_url=ctx.author.avatar_url)
  embed.add_field(name= f"{ctx.author.name}" ,value = text_player + f"\n Total: `{p_sum}`" ,inline=True)
  embed.add_field(name=f"**Dealer Hand**", value= text_dealer+f"\nTotal: `{d_sum}`",inline=True)
  embed.add_field(name=state,value=embed_value,inline=False)

  return embed