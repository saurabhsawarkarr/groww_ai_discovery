with open("scratch_opp_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

import re

# Find JSX text literals or children
children = re.findall(r'children:\s*([^\}]+)', js)
print("Found children:", len(children))

# Print interesting strings
strings = re.findall(r'"([^"\\]{4,120})"', js)
print("Found strings:", len(strings))

keywords = ["opportunity", "priority", "score", "impact", "effort", "risk", "matrix", "bet", "metric", "ranking", "rank", "solution", "experiment", "hypothesis", "tier"]
matched = [s for s in strings if any(k in s.lower() for k in keywords)]
print("\n--- MATCHED STRINGS ---")
for m in set(matched):
    print(" *", m)

