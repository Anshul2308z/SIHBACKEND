import os
import requests

api_key = os.environ.get("OPENAI_API_KEY")
res = requests.post(
    "https://api.openai.com/v1/embeddings",
    headers={"Authorization": f"Bearer {api_key}"},
    json={"model": "text-embedding-3-small", "input": "Hello world"}
)
print("Status:", res.status_code)
print("Response:", res.json())
