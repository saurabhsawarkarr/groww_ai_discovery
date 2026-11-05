with open("scratch_taxonomy_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's search for words like name, definition, evidence_count, confidence_level, etc.
import re

# Find the main component function
# Let's search for "Why Search Fails" and print surrounding 2000 chars
pos = js.find("Why Search Fails")
if pos != -1:
    print("Found 'Why Search Fails' at", pos)
    print("--- Surrounding Code ---")
    print(js[max(0, pos-500):min(len(js), pos+3000)])
else:
    print("Not found")

