with open("scratch_taxonomy_chunk.js", "r", encoding="utf-8") as f:
    code = f.read()

import re
fetches = re.findall(r'fetch\([^\)]+\)', code)
print("Fetches in taxonomy chunk:", fetches)

# Let's search for URLs or paths
paths = re.findall(r'["\'](/[^"\']+)["\']', code)
print("Paths in taxonomy chunk:")
for p in set(paths):
    print(" -", p)

