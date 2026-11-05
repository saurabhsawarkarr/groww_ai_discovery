import urllib.request

base = "https://google-photos-discovery-engine-theta.vercel.app"
url = base + "/_next/static/chunks/app/projects/%5Bid%5D/layout-6025aabe3c0a99ab.js"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    code = resp.read().decode("utf-8")

with open("scratch_layout_chunk.js", "w", encoding="utf-8") as f:
    f.write(code)

print("Downloaded layout chunk, length:", len(code))
import re
paths = set(re.findall(r'["\'](/[^"\']+)["\']', code))
print("Paths in layout chunk:")
for p in paths:
    print(" -", p)

