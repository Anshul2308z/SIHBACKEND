import re
with open("/home/anshul/Desktop/final-sih-frontend/src/routes/abs.tsx", "r") as f:
    text = f.read()

panel_regex = re.compile(r'\{submitted \? \<Panel className="animate-rise p-6"\>.*?\</Panel\> : null\}', re.DOTALL)
new_panel = """{submitted ? <Panel className="animate-rise p-6">
          {loading || !result ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="size-8 animate-spin text-saffron" />
              <p className="mt-4 text-sm text-muted-foreground">{t("Analyzing ABS obligations via LLM...")}</p>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <Eyebrow className="mr-auto">{t("Risk radar output")}</Eyebrow>
                <JurisdictionPill jurisdiction="India" />
              </div>

              <div className="mt-4 flex items-center gap-3">
                <RiskChip level={result.status.level} />
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
with open("/home/anshul/Desktop/final-sih-frontend/src/routes/abs.tsx", "w") as f:
    f.write(text)
