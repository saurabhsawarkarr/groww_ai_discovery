with open("scratch_opp_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's search for the page title and surrounding code
# Let's find h1, h2, or page headers
import re
titles = re.findall(r'h[1-3][^>]*>[^<]+<', js)
print("Titles:", titles)

# Let's find all occurrences of "Opportunity" or "Opportunities"
pos = 0
while True:
    pos = js.find("pportunit", pos)
    if pos == -1:
        break
    print(f"\n--- Match at {pos} ---")
    print(js[max(0, pos-150):min(len(js), pos+400)])
    pos += 10

