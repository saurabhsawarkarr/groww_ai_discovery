import urllib.request
import json

base_url = "https://google-photos-discovery-engine-theta.vercel.app"

# Let's check common Next.js API endpoints or RSC payload
endpoints = [
    "/api/projects/proj_photo_retrieval_2026/taxonomy",
    "/api/projects/proj_photo_retrieval_2026",
    "/api/taxonomy",
    "/projects/proj_photo_retrieval_2026/taxonomy.json",
]

for ep in endpoints:
    url = base_url + ep
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode("utf-8")
            print("SUCCESS:", ep, "length:", len(data))
            try:
                parsed = json.loads(data)
                print("Keys:", list(parsed.keys()) if isinstance(parsed, dict) else len(parsed))
                with open("sample_data.json", "w", encoding="utf-8") as f:
                    f.write(data)
            except:
                print("Not JSON")
    except Exception as e:
        print("Failed:", ep, e)

