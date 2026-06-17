import json

with open(
    "data/pages/www.juit.ac.in_Centre-of-Excellence-in-Structural-Engineering-and-Disaster-Management.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

print(data["title"])
print()
print(data["content"][:1000])
