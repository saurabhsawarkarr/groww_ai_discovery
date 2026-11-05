import urllib.request
import re

base_url = "https://google-photos-discovery-engine-theta.vercel.app"
opp_url = f"{base_url}/projects/proj_photo_retrieval_2026/opportunities"

req = urllib.request.Request(opp_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode("utf-8")

with open("scratch_opp_html.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Downloaded opp HTML, length:", len(html))

chunks = re.findall(r'/_next/static/chunks/[^"]+\.js', html)
print("Found chunks in opp page:", len(chunks))
for c in chunks:
    if "opportunities" in c or "page" in c:
        print("Opportunities chunk:", c)
        c_req = urllib.request.Request(base_url + c, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(c_req) as c_resp:
            chunk_js = c_resp.read().decode("utf-8")
            with open("scratch_opp_chunk.js", "w", encoding="utf-8") as out:
                out.write(chunk_js)
            print("Wrote scratch_opp_chunk.js, length:", len(chunk_js))

