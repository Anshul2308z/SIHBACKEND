import re

with open("/home/anshul/Desktop/final-sih-frontend/src/routes/patents.tsx", "r") as f:
    text = f.read()

# 1. Empty the initial state of the query
text = text.replace('const [query, setQuery] = useState("herbal formulation using turmeric and neem for skin inflammation");', 'const [query, setQuery] = useState("");')

# 2. Add validation inside search()
old_search = """  const search = async () => {
    setLoading(true);
    setRan(true);"""

new_search = """  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setRan(true);"""
text = text.replace(old_search, new_search)

# 3. Remove useEffect
text = re.sub(r'  // Perform initial search on mount\s*useEffect\(\(\) => \{\s*search\(\);\s*// eslint-disable-next-line react-hooks/exhaustive-deps\s*\}, \[\]\);', '', text)

# 4. Disable search button if query is empty
text = text.replace('onClick={search} disabled={loading}', 'onClick={search} disabled={loading || !query.trim()}')

# 5. Fix EmptyState logic
text = text.replace('results.length === 0 ? <EmptyState', '!ran ? <EmptyState title={t("Start your search")} body={t("Enter a concept or formulation above to find relevant patents and prior art.")} /> : results.length === 0 ? <EmptyState')

with open("/home/anshul/Desktop/final-sih-frontend/src/routes/patents.tsx", "w") as f:
    f.write(text)
