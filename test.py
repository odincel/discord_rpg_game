import random

deck = {
  "♦️":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "♣️":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "♥️":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"],
  "♠️":["A",2,3,4,5,6,7,8,9,10,"J","Q","K"]
}
deck_shape = ("♦️","♣️","♥️","♠️")

p_hand = {}
d_hand = {}

for key in deck.keys():
  random.shuffle(deck[key])

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

p_hand = deal(p_hand)
d_hand = deal(d_hand)
p_sum = sum_hand(p_hand)
d_sum = sum_hand(d_hand)


print(f"{p_hand[0]['shape']}{p_hand[0]['num']} {p_hand[1]['shape']}{p_hand[1]['num']}\n{p_sum}")
print(f"{d_hand[0]['shape']}{d_hand[0]['num']} ?\n{d_hand[0]['num']}")
hit=input().lower()
