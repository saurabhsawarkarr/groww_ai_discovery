import urllib.request
import re
import json

base_url = "https://google-photos-discovery-engine-theta.vercel.app"
url = f"{base_url}/projects/proj_photo_retrieval_2026/taxonomy"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")
    
    # Check if there are Next.js data or build chunks
    chunks = re.findall(r'/_next/static/chunks/[^"]+\.js', html)
    print("Found chunks:", len(chunks))
    
    for c in chunks:
        if "taxonomy" in c:
            print("Taxonomy chunk:", c)
            chunk_req = urllib.request.Request(base_url + c, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(chunk_req) as c_resp:
                chunk_js = c_resp.read().decode("utf-8")
                # Look for strings / text inside chunk
                print("Taxonomy chunk length:", len(chunk_js))
                with open("scratch_taxonomy_chunk.js", "w", encoding="utf-8") as out:
                    out.write(chunk_js)
                print("Wrote scratch_taxonomy_chunk.js")
except Exception as e:
    print("Error:", e)

