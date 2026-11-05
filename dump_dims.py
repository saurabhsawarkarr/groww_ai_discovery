with open("scratch_opp_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's search for the definition of h or dimensions
import re
pos = js.find("key:")
print("pos of key:", pos)
# Let's search around key:
for m in re.finditer(r'\{key:"([^"]+)",label:"([^"]+)"', js):
    print("Dimension:", m.group(1), "->", m.group(2))

# Also search for description or type
matches = re.findall(r'\{key:"([^"]+)",label:"([^"]+)",type:"([^"]+)"(?:,description:"([^"]+)")?', js)
for m in matches:
    print("Full Dim:", m)

