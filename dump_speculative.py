with open("scratch_opp_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("Speculative / Emerging Opportunities")
print(js[pos-200:pos+2500])

