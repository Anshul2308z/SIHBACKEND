import re

with open('/home/anshul/Desktop/final-sih-frontend/src/routes/prior-art.tsx', 'r') as f:
    content = f.read()

# Locate the useEffect in PriorArt
old_use_effect = '''  const search = Route.useSearch();
  const [data, setData] = useState<{
    nodes: EvidenceNode[];
    edges: Array<[string, string]>;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetchPriorArtGraph(search.query).then(res => {'''

new_use_effect = '''  const search = Route.useSearch();
  const [data, setData] = useState<{
    nodes: EvidenceNode[];
    edges: Array<[string, string]>;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Fallback to localStorage if accessed via navbar without a query param
    const activeQuery = search.query || localStorage.getItem('last_prior_art_query') || undefined;
    
    if (activeQuery) {
      localStorage.setItem('last_prior_art_query', activeQuery);
    }
    
    fetchPriorArtGraph(activeQuery).then(res => {'''

content = content.replace(old_use_effect, new_use_effect)

# Also update the dependency array of useEffect
old_dep = '}, [search.query]);'
new_dep = '}, [search.query]);' # Actually, search.query is fine, since if it changes, it re-runs.

with open('/home/anshul/Desktop/final-sih-frontend/src/routes/prior-art.tsx', 'w') as f:
    f.write(content)

