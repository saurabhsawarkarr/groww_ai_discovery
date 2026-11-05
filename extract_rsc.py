import urllib.request
import re

url = "https://google-photos-discovery-engine-theta.vercel.app/projects/proj_photo_retrieval_2026/taxonomy"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode("utf-8")

with open("sample_html.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Saved sample_html.html, length:", len(html))

# Extract all __next_f strings
pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.*)"\]\)', html)
print("Found pushes:", len(pushes))
for i, p in enumerate(pushes):
    # unescape
    unescaped = p.encode().decode('unicode_escape')
    with open(f"push_{i}.txt", "w", encoding="utf-8") as f:
        f.write(unescaped)
    print(f"Push {i} length:", len(unescaped))

