import json

with open("src/static/codes.json", "r", encoding="utf-8") as file:
    country_codes = json.loads(file.read())
