with open("scratch_opp_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("What to Build (Feature Opportunities)")
print(js[pos:pos+3500])

