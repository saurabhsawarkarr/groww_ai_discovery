"""Clean up old pilot clusters and synchronize the 7 major themes in discovery_engine.db."""
import sqlite3
from pathlib import Path

db_path = Path("data/database/discovery_engine.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("DELETE FROM thematic_clusters WHERE cluster_id LIKE 'cl_%';")
conn.commit()

rows = c.execute("SELECT cluster_id, title, item_count FROM thematic_clusters ORDER BY item_count DESC;").fetchall()
print(f"Remaining {len(rows)} thematic clusters:")
for r in rows:
    print(f"  {r[0]}: {r[1]} ({r[2]} items)")
conn.close()
