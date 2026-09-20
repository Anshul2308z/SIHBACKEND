import os
import requests

api_key = os.environ.get("GROQ_API_KEY")
res = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key}"})
print("Groq Status:", res.status_code)
