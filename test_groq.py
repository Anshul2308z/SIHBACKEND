import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "groq/compound",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
}
res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
print("groq/compound:", res.status_code, res.text[:200])

payload["model"] = "allam-2-7b"
res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
print("allam-2-7b:", res.status_code, res.text[:200])
