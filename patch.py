with open("/home/anshul/Desktop/final-sih-frontend/src/routes/formulation.tsx", "r") as f:
    text = f.read()

import re
pattern = re.compile(r'\{done \? \<Panel className="animate-rise p-6"\>.*?\</Panel\> : null\}', re.DOTALL)

replacement = """{done ? <Panel className="animate-rise p-6">
              {loading || !result ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="size-8 animate-spin text-saffron" />
                  <p className="mt-4 text-sm text-muted-foreground">{t("Generating classification via LLM...")}</p>
                </div>
              ) : (
                <>
                  <div className="flex flex-wrap items-center gap-2">
                    <Eyebrow className="mr-auto">{t("Preliminary classification")}</Eyebrow>
                    <JurisdictionPill jurisdiction="India" />
                  </div>
                  <h2 className="mt-3 font-display text-2xl text-saffron">{result.label}</h2>
                  <ConfidenceMeter value={result.confidence} className="mt-5" />

                  <Separator className="my-5" />

                  <Eyebrow>{t("Reasoning summary")}</Eyebrow>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{result.reasoning}</p>

                  <div className="mt-5 grid gap-5 sm:grid-cols-2">
                    <div>
                      <Eyebrow>{t("Applicable regulatory route")}</Eyebrow>
                      <p className="mt-1.5 text-sm text-foreground">{result.route}</p>
                    </div>
                    <div>
                      <Eyebrow>{t("Relevant authorities")}</Eyebrow>
                      <div className="mt-1.5 flex flex-wrap gap-2">
                        {result.authorities.map((x: string) => <EvidenceChip key={x}>{x}</EvidenceChip>)}
                      </div>
                    </div>
                  </div>

                  <div className="mt-5">
                    <Eyebrow>{t("Potential IP implications")}</Eyebrow>
                    <div className="mt-1.5 flex flex-wrap gap-2">
                      {result.ip.map((x: string) => <EvidenceChip key={x}>{x}</EvidenceChip>)}
                    </div>
                  </div>

                  <div className="mt-5 flex flex-wrap gap-2">
                    <SourceBadge id="ayush" />
                    <SourceBadge id="tkdl" />
                  </div>
                </>
              )}
            </Panel> : null}"""

new_text = pattern.sub(replacement, text)

with open("/home/anshul/Desktop/final-sih-frontend/src/routes/formulation.tsx", "w") as f:
    f.write(new_text)

