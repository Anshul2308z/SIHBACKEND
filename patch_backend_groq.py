import re

def add_groq(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Replace the LLM instantiation block
    old_block = """            elif LLM_PROVIDER == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            else:
                raise Exception(f"Unsupported LLM for structured output: {LLM_PROVIDER}")"""
                
    new_block = """            elif LLM_PROVIDER == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            elif LLM_PROVIDER == "groq":
                from langchain_groq import ChatGroq
                llm = ChatGroq(model="llama3-8b-8192", temperature=0)
            else:
                raise Exception(f"Unsupported LLM for structured output: {LLM_PROVIDER}")"""
                
    content = content.replace(old_block, new_block)
    
    with open(filepath, "w") as f:
        f.write(content)

add_groq("src/sihbackend/api/abs.py")
add_groq("src/sihbackend/api/formulation.py")
