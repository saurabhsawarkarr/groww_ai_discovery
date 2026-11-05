"""Google Play Store ingestion adapter for the Groww Android application.

Uses google-play-scraper to harvest public user reviews, ratings, and developer
replies, transforming them into standardized RawRecord instances.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from google_play_scraper import Sort, reviews
from google_play_scraper.exceptions import NotFoundError

from src.connectors.base import BaseSourceConnector, RawRecord

logger = logging.getLogger("groww_discovery.connectors.play_store")


class PlayStoreConnector(BaseSourceConnector):
    """Ingestion connector for Google Play Store app reviews."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.app_id = self.config.get("app_id", "com.nextbillion.groww")
        self.lang = self.config.get("lang", "en")
        self.country = self.config.get("country", "in")
        self.default_count = self.config.get("default_count", 200)

    def fetch_records(
        self,
        count: Optional[int] = None,
        sort: Optional[Sort] = None,
        filter_score_with: Optional[int] = None,
        **kwargs
    ) -> List[RawRecord]:
        """Fetch and normalize Google Play reviews for the target app.

        Args:
            count: Number of reviews to request. Defaults to config default_count.
            sort: Sorting order (Sort.NEWEST or Sort.MOST_RELEVANT). Defaults to Sort.NEWEST.
            filter_score_with: Optional filter for star rating (1 to 5).
        """
        target_count = count if count is not None else self.default_count
        target_sort = sort if sort is not None else Sort.NEWEST

        logger.info(
            "Fetching up to %d Play Store reviews for app '%s' (lang=%s, country=%s)",
            target_count, self.app_id, self.lang, self.country
        )

        try:
            raw_reviews, _ = reviews(
                self.app_id,
                lang=self.lang,
                country=self.country,
                sort=target_sort,
                count=target_count,
                filter_score_with=filter_score_with,
            )
        except NotFoundError:
            logger.error("App ID '%s' not found on Google Play Store (%s).", self.app_id, self.country)
            return []
        except Exception as e:
            logger.error("Error fetching Play Store reviews: %s", str(e), exc_info=True)
            return []

        records: List[RawRecord] = []
        for item in raw_reviews:
            review_text = (item.get("content") or "").strip()
            if not review_text:
                continue

            review_id = str(item.get("reviewId") or "")
            if not review_id:
                continue

            pub_date = item.get("at")
            if isinstance(pub_date, datetime):
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)

            thread_ctx = {
                "score": item.get("score"),
                "thumbsUpCount": item.get("thumbsUpCount"),
                "reviewCreatedVersion": item.get("reviewCreatedVersion"),
                "replyContent": item.get("replyContent"),
                "repliedAt": item.get("repliedAt").isoformat() if item.get("repliedAt") else None,
            }

            record = RawRecord(
                raw_id=f"playstore_{self.app_id}_{review_id}",
                source_platform="play_store",
                source_url=f"https://play.google.com/store/apps/details?id={self.app_id}&reviewId={review_id}",
                author_id_hash=self.hash_author(item.get("userName")),
                published_at=pub_date,
                collected_at=datetime.now(timezone.utc),
                raw_text=review_text,
                thread_context=thread_ctx,
                product_context="groww_specific",
            )
            records.append(record)

        logger.info("Successfully ingested and validated %d Play Store records", len(records))
        return records
