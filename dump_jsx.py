import re

with open("scratch_taxonomy_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's see all text constants and UI elements
# In Next.js client component, look for jsx text
texts = re.findall(r'children:\s*([^\}]+)', js)
print("Found children calls:", len(texts))
for t in texts[:30]:
    print("CHILDREN:", t[:120])

