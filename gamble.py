import random
from db import get_database
import discord

def head_tail(ctx):
    db = get_database()["samurai_rpg"]["users"]
    user = db.find_one({"_id":str(ctx.author.id)})
    user_money=user["Gold"]
    user_text = "".join([i for i in ctx.content.lower().replace("cf ","").replace(" ","") if not i.isdigit()])
    
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
