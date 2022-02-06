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
for i in range(1,100):
    need = round(xp*mult**(i-1))*round(piece*mult**(i-1))
    total+=need
    level_list[i+1] = {
        "piece":round(xp*mult**(i-1)),
        "xp":round(piece*mult**(i-1)),
        "total_xp":total
    }

jsonString = json.dumps(level_list,indent = 4)
jsonFile = open("levels.json", "w")
jsonFile.write(jsonString)
jsonFile.close()