import json 

piece=20
xp=10
mult=1.05
total = 0

level_list = {
    1:{
        "piece":0,
        "xp":0,
        "total_xp":0
    }
}
for i in range(2,100):
    need = round(xp*mult**(i))*round(piece*(mult+0.1)**(i))
    total+=need
    level_list[i+1] = {
        "piece":round(piece*(mult+0.1)**(i)),
        "xp":round(xp*mult**(i)),
        "total_xp":total
    }

jsonString = json.dumps(level_list,indent = 4)
jsonFile = open("levels.json", "w")
jsonFile.write(jsonString)
jsonFile.close()