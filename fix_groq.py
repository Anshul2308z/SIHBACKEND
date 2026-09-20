import re

def fix_groq(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Replace the invalid model string
    content = content.replace('ChatGroq(model="llama3-8b-8192"', 'ChatGroq(model="llama-3.1-8b-instant"')
    
    with open(filepath, "w") as f:
        f.write(content)

fix_groq("src/sihbackend/api/abs.py")
fix_groq("src/sihbackend/api/formulation.py")
