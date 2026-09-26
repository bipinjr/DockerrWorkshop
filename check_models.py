import os, json
from dotenv import load_dotenv
load_dotenv()
import requests

key = os.getenv("GROQ_API_KEY")
headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}
r = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=15)
data = r.json().get("data", [])
names = [m["id"] for m in data]
print("TOTAL:", len(names))
print()
for n in names:
    print(n)
