import requests
from bs4 import BeautifulSoup

url = "https://www.juit.ac.in/juit-youth-club"

html = requests.get(url).text

with open("page.html", "w", encoding="utf-8") as f:
    f.write(html)

print("saved")
