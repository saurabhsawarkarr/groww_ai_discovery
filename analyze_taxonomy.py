with open("scratch_taxonomy_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

import re

# Let's extract the full component code or de-minify parts of it
# Look for the main render function
print("Searching for UI elements...")

# Look for titles, badges, cards, metrics, buttons
card_parts = re.findall(r'(\.card[^\;]+)', js)
print("Card references:", len(card_parts))

# Let's extract all text literals in the component
literals = re.findall(r'>([^<>{}"\']+)<', js)
print("Literals:", len(literals))

# Let's write a formatted view of the JSX / structure
with open("taxonomy_component_analysis.txt", "w", encoding="utf-8") as out:
    # Find all object properties or JSX tags
    tags = re.findall(r'(\([0-9],[a-zA-Z]\.jsx[s]?\)\([^\)]+\))', js)
    out.write(f"Found tags: {len(tags)}\n\n")
    for t in tags[:100]:
        out.write(t + "\n---\n")

print("Wrote taxonomy_component_analysis.txt")

