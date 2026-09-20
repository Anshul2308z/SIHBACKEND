def fix_groq(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    content = content.replace('ChatGroq(model="groq/compound"', 'ChatGroq(model="qwen/qwen3.8-27b"')
    content = content.replace('ChatGroq(model="llama-3.1-8b-instant"', 'ChatGroq(model="qwen/qwen3.8-27b"')
    content = content.replace('ChatGroq(model="llama3-8b-8192"', 'ChatGroq(model="qwen/qwen3.8-27b"')
    
    with open(filepath, "w") as f:
        f.write(content)

for p in ["src/sihbackend/api/abs.py", "src/sihbackend/api/formulation.py", "src/sihbackend/services/chat_service.py"]:
    fix_groq(p)
