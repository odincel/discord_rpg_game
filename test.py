import json 
import random

f = json.load(open("data/enemy.json"))
for i in range(1,101):
    count = 0
    for j in f.keys():
        if f[j]["level"] == i:
            count += 1
    if count < 4 and count != 0:
        print(i,count)
print("Finish")

enemy_dict = json.load(open("data/enemy.json"))
level_dict = dict()
for enemy in enemy_dict.keys():
  level_dict[enemy] = enemy_dict[enemy]["level"]

def get_enemy(player):
  player = player // 5 + 1
  print(player)
  enemys = dict((k, v) for k, v in level_dict.items() if v == player) 
  selected = random.choice(list(enemys.keys()))
  return selected

print(get_enemy(40))