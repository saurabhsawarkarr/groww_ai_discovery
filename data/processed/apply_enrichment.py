import sqlite3
import json
from pathlib import Path
from enrich_behaviour import enrich_record

db_path = Path("data/database/discovery_engine.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. Fetch all records from extracted_evidence joined with raw_conversations
c.execute("""
    SELECT 
        e.evidence_id, 
        e.raw_id, 
        e.journey_stage, 
        e.reported_behaviour, 
        e.friction_or_concern, 
        e.evidence_quote, 
        r.raw_text
    FROM extracted_evidence e
    JOIN raw_conversations r ON e.raw_id = r.raw_id;
""")
rows = c.fetchall()
print(f"Total extracted evidence rows to enrich: {len(rows)}")

updated_count = 0
enriched_records = []

for r in rows:
    eid, raw_id, stage, beh, fric, quote, raw_text = r
    enriched = enrich_record(eid, raw_text, quote, stage, beh, fric)
    
    # Update SQLite database
    c.execute("""
        UPDATE extracted_evidence
        SET 
            journey_stage = ?,
            reported_behaviour = ?,
            friction_or_concern = ?,
            trigger_or_situation = ?,
            workaround = ?,
            reported_outcome = ?
        WHERE evidence_id = ?;
    """, (
        enriched["journey_stage"],
        enriched["reported_behaviour"],
        enriched["friction_or_concern"],
        enriched["trigger_or_situation"],
        enriched["workaround"],
        enriched["reported_outcome"],
        eid,
    ))
    updated_count += 1

conn.commit()
print(f"Successfully updated {updated_count} rows in extracted_evidence in SQLite.")

# 2. Also update data/processed/extracted_evidence.json if present
json_path = Path("data/processed/extracted_evidence.json")
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data:
        eid = item.get("evidence_id")
        # Fetch updated values from DB
        c.execute("""
            SELECT journey_stage, reported_behaviour, friction_or_concern, trigger_or_situation, workaround, reported_outcome
            FROM extracted_evidence WHERE evidence_id = ?;
        """, (eid,))
        row = c.fetchone()
        if row:
            item["journey_stage"] = row[0]
            item["reported_behaviour"] = row[1]
            item["friction_or_concern"] = row[2]
            item["trigger_or_situation"] = row[3]
            item["workaround"] = row[4]
            item["reported_outcome"] = row[5]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Successfully synchronized {len(data)} items in {json_path}")

conn.close()

# Print sample enriched records to verify
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("""
    SELECT evidence_id, journey_stage, reported_behaviour, friction_or_concern, trigger_or_situation, workaround, evidence_quote 
    FROM extracted_evidence 
    LIMIT 8;
""")
sample_rows = c.fetchall()
print("\n=== VERIFIED SAMPLE ENRICHED RECORDS ===")
for idx, s in enumerate(sample_rows):
    print(f"\n--- RECORD {idx+1} [{s[0]}] ---")
    print(f"Stage: {s[1]}")
    print(f"Reported Behaviour: {s[2]}")
    print(f"Friction / Concern: {s[3]}")
    print(f"Trigger / Situation: {s[4]}")
    print(f"Workaround: {s[5]}")
    print(f"Quote: {s[6][:90]}...")

conn.close()
