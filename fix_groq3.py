def fix_groq(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Replace the invalid model string
    content = content.replace('ChatGroq(model="qwen/qwen3.8-27b"', 'ChatGroq(model="groq/compound"')
    
    with open(filepath, "w") as f:
        f.write(content)

fix_groq("src/sihbackend/services/chat_service.py")
