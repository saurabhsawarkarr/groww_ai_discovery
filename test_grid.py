import json
from pathlib import Path

json_path = Path("data/processed/major_themes_3k_discovery.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

themes = data["themes"]
total_corpus_count = data.get("total_analyzed_corpus", 3052)
print("Loaded themes:", len(themes))

cards = []
for i, t in enumerate(themes, 1):
    cid = t.get("theme_id", f"THEME-{i}")
    title = t.get("name", "Untitled Theme")
    desc = t.get("core_problem", "")
    item_count = t.get("prevalence_count", 0)
    prevalence_pct = t.get("prevalence_percentage", 0.0)
    quotes = t.get("representative_quotes", [])
    platforms = t.get("platform_breakdown", {})
    cards.append(cid + ": " + title)

print("Verified all cards:", len(cards))

