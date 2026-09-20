with open("/home/anshul/Desktop/final-sih-frontend/src/routes/abs.tsx", "r") as f:
    text = f.read()

old_fetch = """      const res = await fetch(`${API_BASE_URL}/api/v1/compliance/abs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resource, origin, collection, tk, commercial, patent, exportMarket
        })
      });
      const data = await res.json();
      setResult(data);"""

new_fetch = """      const res = await fetch(`${API_BASE_URL}/api/v1/compliance/abs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resource, origin, collection, tk, commercial, patent, exportMarket
        })
      });
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setResult(data);"""

text = text.replace(old_fetch, new_fetch)

# Make sure resource isn't empty to submit
text = text.replace('onClick={checkAbs} disabled={loading}', 'onClick={checkAbs} disabled={loading || !resource.trim()}')

with open("/home/anshul/Desktop/final-sih-frontend/src/routes/abs.tsx", "w") as f:
    f.write(text)
