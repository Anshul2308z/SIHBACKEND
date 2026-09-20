import os
import requests

api_key = os.environ.get("GEMINI_API_KEY")
res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
print(res.json())
