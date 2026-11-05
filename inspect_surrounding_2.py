with open("scratch_taxonomy_chunk.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("Why Search Fails")
print(js[pos+2500:pos+6000])

