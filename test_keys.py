import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Test Gemini
gemini_key = os.environ.get("GEMINI_API_KEY")
print(f"Gemini Key: {gemini_key[:5]}...{gemini_key[-5:]}" if gemini_key else "No Gemini Key")
res = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={gemini_key}",
    json={"model": "models/text-embedding-004", "content": {"parts": [{"text": "Hello world"}]}}
)
print("Gemini Status:", res.status_code)
if res.status_code != 200: print(res.json())

# Test OpenAI
openai_key = os.environ.get("OPENAI_API_KEY")
print(f"\nOpenAI Key: {openai_key[:5]}...{openai_key[-5:]}" if openai_key else "No OpenAI Key")
res2 = requests.post(
    "https://api.openai.com/v1/embeddings",
    headers={"Authorization": f"Bearer {openai_key}"},
    json={"model": "text-embedding-3-small", "input": "Hello world"}
)
print("OpenAI Status:", res2.status_code)
if res2.status_code != 200: print(res2.json())

