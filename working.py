import json

with open("F:\Resu-Control-Unit\working.json") as f:
    data = f.read()
    
data = json.loads(data)

for heading in data:
    for i in data[heading]:
            for j in range(0,14):
                    if data[heading][i][j]== '(0, 0, 0)':
                            data[heading][i][j] = "0"
                            data[heading][i] = "0"
                    else:
                            data[heading][i][j] = "0"
                            data[heading][i][j] = "x"
    for e in range(0,15):
        data[heading][e+15] = data[heading][e]
                            
print(json.dumps(data))

with open("F:\Resu-Control-Unit\working2.json", "w") as e:
    e.write(json.dumps(data))
    