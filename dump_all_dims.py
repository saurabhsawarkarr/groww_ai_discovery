with open("scratch_opp_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("evidence_frequency")
print(js[pos-200:pos+1500])

