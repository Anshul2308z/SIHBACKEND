import os
from dotenv import load_dotenv
load_dotenv()
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
result = client.models.embed_content(
    model="text-embedding-004",
    contents="Hello world!"
)
print("Embedding length:", len(result.embeddings[0].values))
