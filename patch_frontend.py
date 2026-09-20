import re

with open('/home/anshul/Desktop/final-sih-frontend/src/routes/formulation.tsx', 'r') as f:
    content = f.read()

# Safe map
content = content.replace(
    '{result.authorities.map(x => <EvidenceChip key={x}>{x}</EvidenceChip>)}',
    '{(Array.isArray(result?.authorities) ? result.authorities : []).map(x => <EvidenceChip key={x}>{x}</EvidenceChip>)}'
)
content = content.replace(
    '{result.ip.map(x => <EvidenceChip key={x}>{x}</EvidenceChip>)}',
    '{(Array.isArray(result?.ip) ? result.ip : []).map(x => <EvidenceChip key={x}>{x}</EvidenceChip>)}'
)

with open('/home/anshul/Desktop/final-sih-frontend/src/routes/formulation.tsx', 'w') as f:
    f.write(content)

