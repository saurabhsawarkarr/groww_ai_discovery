import re

with open("scratch_taxonomy_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

# Find strings or interesting text
strings = re.findall(r'"([^"\\]{4,100})"', js)
print("Total strings:", len(strings))

# Filter interesting strings
keywords = ["theme", "taxonomy", "cluster", "evidence", "quote", "prevalence", "filter", "card", "category", "finding", "search", "view", "level", "tier"]
matches = [s for s in strings if any(k in s.lower() for k in keywords)]
print("Matched keywords:", len(matches))
for m in matches[:60]:
    print(" -", m)

