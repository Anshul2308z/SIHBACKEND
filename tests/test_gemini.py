import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from google import genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

class TestOutput(BaseModel):
    answer: str

model_to_test = "gemini-3.6-flash"
print(f"Testing model: {model_to_test} via LangChain")

try:
    llm = ChatGoogleGenerativeAI(model=model_to_test, temperature=0, google_api_key=api_key)
    structured_llm = llm.with_structured_output(TestOutput)
    res = structured_llm.invoke("Hi, what is your name?")
    print(f"Success! Output: {res}")
except Exception as e:
    print(f"Error invoking model: {e}")
