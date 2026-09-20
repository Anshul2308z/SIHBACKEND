import os
import requests

api_key = os.environ.get("GEMINI_API_KEY")
res = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}",
    json={"model": "models/text-embedding-004", "content": {"parts": [{"text": "Hello world"}]}}
)
print("Status:", res.status_code)
print("Response:", res.json())
