import sqlite3

conn = sqlite3.connect('data/database/discovery_engine.db')
c = conn.cursor()
c.execute('''
    SELECT evidence_id, journey_stage, reported_behaviour, friction_or_concern, trigger_or_situation, workaround, evidence_quote 
    FROM extracted_evidence 
    LIMIT 10;
''')
rows = c.fetchall()
for i, r in enumerate(rows):
    print(f"--- RECORD {i+1} [{r[0]}] ---")
    print(f"Stage: {r[1]}")
    print(f"Reported Behaviour: {r[2]}")
    print(f"Friction / Concern: {r[3]}")
    print(f"Trigger / Situation: {r[4]}")
    print(f"Workaround: {r[5]}")
    print(f"Quote: {r[6][:100]}...")
conn.close()
