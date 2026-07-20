from pathlib import Path
import json
from collections import Counter

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "pages"

counter = Counter()

total = 0

for file in DATA_DIR.glob("*.json"):

    total += 1

    with open(file, encoding="utf-8") as f:
        page = json.load(f)

    title = page.get("title", "").lower()
    url = page.get("url", "").lower()
    h1 = page.get("h1", "").lower()

    text = f"{title} {url} {h1}"

    if "faculty" in text:
        counter["Faculty"] += 1

    if "department" in text:
        counter["Departments"] += 1

    if "hostel" in text:
        counter["Hostels"] += 1

    if "placement" in text:
        counter["Placements"] += 1

    if "research" in text or "centre" in text or "center" in text:
        counter["Research Centres"] += 1

    if "committee" in text:
        counter["Committees"] += 1

    if "scholarship" in text:
        counter["Scholarships"] += 1

    if "fee" in text:
        counter["Fees"] += 1

    if "admission" in text:
        counter["Admissions"] += 1

    if "library" in text:
        counter["Library"] += 1

    if "dispensary" in text or "health" in text:
        counter["Health"] += 1

print("\n========== JUIT KNOWLEDGE AUDIT ==========\n")

print(f"Total pages indexed : {total}\n")

for k in sorted(counter):
    print(f"{k:<20} {counter[k]}")

print("\n==========================================")