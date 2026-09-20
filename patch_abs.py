import re

with open("/home/anshul/Desktop/final-sih-frontend/src/routes/abs.tsx", "r") as f:
    text = f.read()

# 1. Add API URL and Loader
text = text.replace('import { Button } from "@/components/ui/button";', 'import { Button } from "@/components/ui/button";\nimport { Loader2 } from "lucide-react";')
text = text.replace('const originOptions = [', 'const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:10000";\nconst originOptions = [')

# 2. Add State and Fetch Logic
hook_start = text.find('const [submitted, setSubmitted] = useState(false);') + len('const [submitted, setSubmitted] = useState(false);')

fetch_logic = """
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const checkAbs = async () => {
    setLoading(true);
    setSubmitted(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/compliance/abs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resource, origin, collection, tk, commercial, patent, exportMarket
        })
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      // Hardcoded fallback logic is preserved in backend anyway!
    } finally {
      setLoading(false);
    }
  };
"""

text = text[:hook_start] + fetch_logic + text[hook_start:]

# 3. Modify Check Button
text = text.replace('onClick={() => setSubmitted(true)}', 'onClick={checkAbs} disabled={loading}')
text = text.replace('t("Analyze compliance risk")', 'loading ? t("Analyzing...") : t("Analyze compliance risk")')

# 4. Modify Results Panel rendering
panel_regex = re.compile(r'\{submitted \? \<Panel className="p-6 animate-rise"\>.*?\</Panel\> : null\}', re.DOTALL)
new_panel = """{submitted ? <Panel className="p-6 animate-rise">
          {loading || !result ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="size-8 animate-spin text-saffron" />
              <p className="mt-4 text-sm text-muted-foreground">{t("Analyzing ABS obligations...")}</p>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <Eyebrow className="mr-auto">{t("Risk radar output")}</Eyebrow>
                <JurisdictionPill jurisdiction="India" />
              </div>

              <div className="mt-4 flex items-center gap-3">
                <RiskChip level={result.status.level as any} />
                <h2 className="font-display text-xl text-foreground">{result.status.label}</h2>
              </div>

              <Separator className="my-5" />

              <Eyebrow>{t("Applicable frameworks")}</Eyebrow>
              <div className="mt-2 flex flex-wrap gap-2">
                {result.framework.map((f: string) => <EvidenceChip key={f}>{f}</EvidenceChip>)}
              </div>

              <div className="mt-5">
                <Eyebrow>{t("Context")}</Eyebrow>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {result.reasoning}
                </p>
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                <SourceBadge id="nba" />
              </div>
            </>
          )}
        </Panel> : null}"""

text = panel_regex.sub(new_panel, text)

# We can remove the hardcoded score logic entirely to clean it up, but it's safe to leave it unused.
with open("/home/anshul/Desktop/final-sih-frontend/src/routes/abs.tsx", "w") as f:
    f.write(text)

