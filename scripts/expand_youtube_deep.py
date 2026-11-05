"""Deep YouTube harvester for mutual fund, SIP, and Groww app comments.

Discovers hundreds of targeted SIP video guides and extracts authentic
viewer comments, doubts, and frictions with direct canonical URLs.
Zero LLM dependencies.
"""

from datetime import datetime, timezone
import hashlib
import json
from itertools import islice
import logging
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from youtube_comment_downloader import YoutubeCommentDownloader
from src.database.connection import get_connection, get_db_path, init_db
from src.connectors.base import RawRecord
from scripts.download_all_data import export_downloaded_catalog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("groww_discovery.youtube_deep")


def hash_author(author_name: str, salt: str = "groww_privacy_salt_v1") -> str:
    raw = f"{salt}:{author_name or 'anonymous'}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def get_existing_ids(db_path) -> set:
    conn = get_connection(db_path)
    try:
        c = conn.cursor()
        c.execute("SELECT raw_id FROM raw_conversations;")
        return {r[0] for r in c.fetchall()}
    finally:
        conn.close()


SEARCH_QUERIES = [
    "groww mutual fund review 2026",
    "groww sip beginner tutorial hindi",
    "groww xirr negative returns explained",
    "groww sip auto pay setup mandate problem",
    "how to stop pause sip in groww",
    "groww sip cancellation problem",
    "groww mutual fund hidden charges",
    "groww sip debit date change without penalty",
    "first time mutual fund investing mistakes india",
    "groww nav allocation delay problem",
    "pranjal kamra mutual funds for beginners",
    "labour law advisor mutual fund sip guide",
    "asset yogi mutual fund beginner groww",
    "groww demat account charges mutual fund",
    "best sip for beginners groww 2026",
    "zerodha coin vs groww mutual fund"
]


def discover_video_ids(queries: list, max_per_query: int = 15) -> list:
    """Search YouTube web frontend to discover relevant video IDs."""
    logger.info("Discovering YouTube video IDs across %d targeted queries...", len(queries))
    seen_vids = set()
    ordered_vids = []

    for q in queries:
        try:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8")
                matches = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
                added_for_q = 0
                for m in matches:
                    if m not in seen_vids:
                        seen_vids.add(m)
                        ordered_vids.append(m)
                        added_for_q += 1
                        if added_for_q >= max_per_query:
                            break
            logger.info("Query '%s': found %d new video IDs", q, added_for_q)
            time.sleep(0.5)
        except Exception as e:
            logger.debug("Failed searching for '%s': %s", q, str(e))

    logger.info("Total unique YouTube video IDs discovered: %d", len(ordered_vids))
    return ordered_vids


def harvest_comments_from_videos(video_ids: list, seen_ids: set, target_per_vid: int = 60, max_total: int = 3500) -> list:
    """Harvest viewer comments across discovered video IDs."""
    logger.info("Starting comment extraction across up to %d videos (target: %d total)...", len(video_ids), max_total)
    downloader = YoutubeCommentDownloader()
    collected = []

    for idx, vid in enumerate(video_ids, 1):
        if len(collected) >= max_total:
            logger.info("Reached maximum total comment target (%d). Stopping.", max_total)
            break

        video_url = f"https://www.youtube.com/watch?v={vid}"
        try:
            comments_gen = downloader.get_comments_from_url(video_url)
            batch = list(islice(comments_gen, target_per_vid))
            new_in_vid = 0

            for c in batch:
                cid = c.get("cid")
                text = (c.get("text") or "").strip()
                if not cid or not text or len(text.split()) < 3:
                    continue

                raw_id = f"youtube_{vid}_{cid}"
                if raw_id in seen_ids:
                    continue
                seen_ids.add(raw_id)

                source_url = f"https://www.youtube.com/watch?v={vid}&lc={cid}"

                thread_ctx = {
                    "video_id": vid,
                    "comment_id": cid,
                    "votes": c.get("votes", 0),
                    "heart": c.get("heart", False),
                    "time_text": c.get("time", ""),
                }

                record = RawRecord(
                    raw_id=raw_id,
                    source_platform="youtube",
                    source_url=source_url,
                    author_id_hash=hash_author(c.get("author")),
                    published_at=datetime.now(timezone.utc),
                    collected_at=datetime.now(timezone.utc),
                    raw_text=text,
                    thread_context=thread_ctx,
                    product_context="groww_specific" if "groww" in text.lower() else "category_level",
                )
                collected.append(record)
                new_in_vid += 1

            logger.info("[%d/%d] Video %s: +%d comments (Total new YouTube: %d / %d)", idx, len(video_ids), vid, new_in_vid, len(collected), max_total)
            time.sleep(0.7)  # Safe delay between videos
        except Exception as e:
            logger.debug("[%d/%d] Error on video %s: %s", idx, len(video_ids), vid, str(e))

    return collected


def persist_records(records: list, db_path) -> int:
    if not records:
        return 0
    conn = get_connection(db_path)
    inserted = 0
    try:
        c = conn.cursor()
        for r in records:
            try:
                c.execute(
                    """
                    INSERT OR IGNORE INTO raw_conversations 
                    (raw_id, source_platform, source_url, author_id_hash, published_at, collected_at, raw_text, thread_context, product_context, is_qualified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    r.to_db_tuple(is_qualified=0),
                )
                if c.rowcount > 0:
                    inserted += 1
            except Exception as e:
                logger.error("Error inserting %s: %s", r.raw_id, str(e))
        conn.commit()
    finally:
        conn.close()
    return inserted


def main():
    db_file = get_db_path()
    init_db(db_file)

    print("\n" + "=" * 80)
    print("  DEEP YOUTUBE DATA EXPANSION PIPELINE")
    print("  Mode: Broad Query Search & Live Comment Scraping with 100% Direct Links")
    print("=" * 80)

    seen_ids = get_existing_ids(db_file)
    print(f"Existing records in SQLite: {len(seen_ids)}")

    start_time = time.time()

    # 1. Discover top relevant video IDs across 16 diverse queries
    video_ids = discover_video_ids(SEARCH_QUERIES, max_per_query=12)

    # 2. Harvest comments from discovered videos
    new_youtube_records = harvest_comments_from_videos(video_ids, seen_ids, target_per_vid=75, max_total=3000)

    print(f"\n[INFO] Total newly harvested YouTube comments: {len(new_youtube_records)}")

    # 3. Persist to SQLite
    inserted = persist_records(new_youtube_records, db_file)
    print(f"[SUCCESS] Committed {inserted} new YouTube records to SQLite.")

    # 4. Re-export master catalogs to JSON & CSV
    raw_dir = PROJECT_ROOT / "data" / "raw"
    export_downloaded_catalog(db_file, raw_dir)

    # 5. Verification audit
    conn = get_connection(db_file)
    try:
        c = conn.cursor()
        c.execute("SELECT count(*), count(source_url) FROM raw_conversations;")
        tot, with_url = c.fetchone()

        print("\n" + "-" * 80)
        print("  UPDATED DATABASE LINK AUDIT")
        print("-" * 80)
        print(f"  Total Records in Database:         {tot}")
        print(f"  Records with Valid Canonical Link: {with_url} ({(with_url/tot)*100:.1f}%)")
        print("\n  Updated Platform Breakdown:")
        c.execute("SELECT source_platform, count(*), count(source_url) FROM raw_conversations GROUP BY source_platform ORDER BY count(*) DESC;")
        for p, count_p, url_p in c.fetchall():
            print(f"    - {p:15s}: {count_p:6d} records | {url_p:6d} with links ({(url_p/count_p)*100:.1f}%)")
        print("-" * 80)
    finally:
        conn.close()

    elapsed = time.time() - start_time
    print(f"Deep YouTube expansion completed in {elapsed:.1f} seconds.\n")


if __name__ == "__main__":
    main()
