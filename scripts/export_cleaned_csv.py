"""Export the 3,052 cleaned, qualified Mutual Fund SIP conversations to CSV."""

import csv
import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "database" / "discovery_engine.db"
OUTPUT_CSV = PROJECT_ROOT / "data" / "processed" / "cleaned_3k_sip_conversations.csv"

def export_to_csv():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT raw_id, source_platform, source_url, published_at, product_context, thread_context, raw_text
        FROM raw_conversations
        WHERE is_qualified = 1
        ORDER BY source_platform, published_at DESC;
    """)
    rows = c.fetchall()
    conn.close()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "index",
            "raw_id",
            "platform",
            "source_url",
            "published_at",
            "product_context",
            "thread_title_or_video",
            "cleaned_investor_text",
        ])

        for idx, row in enumerate(rows, 1):
            raw_id, plat, url, pub_at, prod_ctx, ctx_json, text = row
            title = ""
            if ctx_json:
                try:
                    ctx = json.loads(ctx_json) if isinstance(ctx_json, str) else ctx_json
                    title = ctx.get("parent_title") or ctx.get("video_title") or ""
                except Exception:
                    pass

            writer.writerow([
                idx,
                raw_id,
                plat,
                url or "",
                str(pub_at or ""),
                prod_ctx or "unknown",
                title,
                text or "",
            ])

    print(f"Exported {len(rows)} records to {OUTPUT_CSV}")

if __name__ == "__main__":
    export_to_csv()
