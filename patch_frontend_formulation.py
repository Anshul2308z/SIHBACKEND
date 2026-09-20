with open("/home/anshul/Desktop/final-sih-frontend/src/routes/formulation.tsx", "r") as f:
    text = f.read()

old_fetch = """      const res = await fetch(`${API_BASE_URL}/api/v1/analyze/formulation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(answers)
      });
      const data = await res.json();
      setResult(data);"""

new_fetch = """      const res = await fetch(`${API_BASE_URL}/api/v1/analyze/formulation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(answers)
      });
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setResult(data);"""

text = text.replace(old_fetch, new_fetch)

with open("/home/anshul/Desktop/final-sih-frontend/src/routes/formulation.tsx", "w") as f:
    f.write(text)
