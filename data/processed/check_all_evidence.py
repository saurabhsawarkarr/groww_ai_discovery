import sqlite3

conn = sqlite3.connect('data/database/discovery_engine.db')
c = conn.cursor()
c.execute('SELECT evidence_id, journey_stage, reported_behaviour, friction_or_concern, evidence_quote FROM extracted_evidence;')
rows = c.fetchall()

for idx, r in enumerate(rows):
    quote = (r[4] or "")[:80]
    print(f"{idx+1}. [{r[0]}] Stage:{r[1]} | Beh:{r[2]} | Fric:{r[3]} | Q:{quote}")

conn.close()
