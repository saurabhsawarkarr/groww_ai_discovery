"""Apple App Store ingestion adapter for the Groww iOS application.

Uses app-store-scraper to pull iOS customer reviews and ratings, transforming
them into normalized RawRecord instances with full metadata traceability.
"""

from datetime import datetime, timezone
import hashlib
import logging
from typing import Any, Dict, List, Optional
try:
    from app_store_scraper import AppStore
except ImportError:
    AppStore = None

from src.connectors.base import BaseSourceConnector, RawRecord

logger = logging.getLogger("groww_discovery.connectors.app_store")


class AppStoreConnector(BaseSourceConnector):
    """Ingestion connector for Apple App Store reviews."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.app_name = self.config.get("app_name", "groww")
        self.app_id = int(self.config.get("app_id", 1404871703))
        self.country = self.config.get("country", "in")
        self.default_count = self.config.get("default_count", 50)

    def fetch_records(
        self,
        how_many: Optional[int] = None,
        after: Optional[datetime] = None,
        **kwargs
    ) -> List[RawRecord]:
        """Fetch and normalize iOS reviews from the Apple App Store.

        Args:
            how_many: Total reviews to harvest. Defaults to default_count.
            after: Optional datetime filter to ignore reviews published prior to date.
        """
        target_count = how_many if how_many is not None else self.default_count
        logger.info(
            "Fetching up to %d App Store reviews for '%s' (id=%d, country=%s)",
            target_count, self.app_name, self.app_id, self.country
        )

        records: List[RawRecord] = []
        raw_reviews = []

        # 1. Attempt official iTunes RSS Customer Reviews endpoint
        try:
            import urllib.request
            import json as pyjson
            seen_ids = set()

            for sort_order in ["mostrecent", "mosthelpful"]:
                for page in range(1, 11):
                    url = f"https://itunes.apple.com/{self.country}/rss/customerreviews/page={page}/id={self.app_id}/sortby={sort_order}/json"
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                        with urllib.request.urlopen(req, timeout=6) as resp:
                            data = pyjson.loads(resp.read().decode("utf-8"))
                            entries = data.get("feed", {}).get("entry", [])
                            for entry in entries:
                                rid = entry.get("id", {}).get("label")
                                if not rid or rid in seen_ids:
                                    continue
                                seen_ids.add(rid)

                                title = entry.get("title", {}).get("label", "")
                                content = entry.get("content", {}).get("label", "")
                                author = entry.get("author", {}).get("name", {}).get("label", "Anonymous")
                                rating_str = entry.get("im:rating", {}).get("label", "5")
                                vote_cnt = entry.get("im:voteCount", {}).get("label", "0")

                                review_text = f"{title}\n{content}".strip() if title else content.strip()
                                if not review_text:
                                    continue

                                pub_date = datetime.now(timezone.utc)
                                updated_str = entry.get("updated", {}).get("label")
                                if updated_str:
                                    try:
                                        pub_date = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                                    except Exception:
                                        pass

                                thread_ctx = {
                                    "title": title,
                                    "rating": int(rating_str) if rating_str.isdigit() else 5,
                                    "vote_count": int(vote_cnt) if vote_cnt.isdigit() else 0,
                                    "app_id": self.app_id,
                                    "sort_order": sort_order,
                                }

                                record = RawRecord(
                                    raw_id=f"appstore_{self.app_id}_{rid}",
                                    source_platform="app_store",
                                    source_url=f"https://apps.apple.com/{self.country}/app/groww-stocks-mutual-funds-upi/id{self.app_id}#review-{rid}",
                                    author_id_hash=self.hash_author(author),
                                    published_at=pub_date,
                                    collected_at=datetime.now(timezone.utc),
                                    raw_text=review_text,
                                    thread_context=thread_ctx,
                                    product_context="groww_specific",
                                )
                                records.append(record)
                    except Exception as page_err:
                        logger.debug("Failed fetching App Store RSS page %d: %s", page, str(page_err))
                        break
        except Exception as rss_err:
            logger.warning("iTunes RSS fetch error: %s. Attempting fallback scraper...", str(rss_err))

        # 2. If RSS didn't yield records, attempt app-store-scraper fallback
        if not records and AppStore is not None:
            try:
                scraper = AppStore(
                    country=self.country,
                    app_name=self.app_name,
                    app_id=self.app_id
                )
                scraper.review(how_many=target_count, after=after)
                raw_reviews = scraper.reviews or []
                for item in raw_reviews:
                    review_text = (item.get("review") or "").strip()
                    if not review_text:
                        continue
                    pub_date = item.get("date")
                    if isinstance(pub_date, datetime) and pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=timezone.utc)
                    date_str = pub_date.isoformat() if pub_date else "nodate"
                    content_hash = hashlib.sha256(f"{date_str}_{review_text}".encode()).hexdigest()[:12]
                    raw_id = f"appstore_{self.app_id}_{content_hash}"
                    thread_ctx = {
                        "title": item.get("title"),
                        "rating": item.get("rating"),
                        "isEdited": item.get("isEdited"),
                        "app_name": self.app_name,
                    }
                    record = RawRecord(
                        raw_id=raw_id,
                        source_platform="app_store",
                        source_url=f"https://apps.apple.com/{self.country}/app/groww/id{self.app_id}",
                        author_id_hash=self.hash_author(item.get("userName")),
                        published_at=pub_date,
                        collected_at=datetime.now(timezone.utc),
                        raw_text=review_text,
                        thread_context=thread_ctx,
                        product_context="groww_specific",
                    )
                    records.append(record)
            except Exception as e:
                logger.error("Error fetching App Store reviews with scraper: %s", str(e))

        logger.info("Successfully ingested %d App Store records", len(records))
        return records
