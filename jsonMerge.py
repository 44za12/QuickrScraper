import os, json
import pandas as pd

if os.path.exists("final.json"):
    os.remove("final.json")

if os.path.exists("final.csv"):
    os.remove("final.csv")

json_files = [pos_json for pos_json in os.listdir(".") if pos_json.endswith('.json')]
final = []
ret = []
uniques = set()

for i in json_files:
    with open(i, "r") as f:
        final.extend(json.loads(f.read()))

for i in final:
    temp = {}
    if i["Mobile"] not in uniques:
        uniques.add(i['Mobile'])
        for key, val in i.items():
            if not key == "Plumber Type":
                newVal = ' '.join(val.strip().replace("\n","").split()) if val else None
                temp[key] = newVal
        ret.append(temp)
    else:
        continue


with open("final.json","w") as f:
    print(len(ret))
    f.write(json.dumps(ret))

df = pd.read_json("final.json")
df.to_csv("final.csv", index=False)