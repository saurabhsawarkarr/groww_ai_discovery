"""Reddit ingestion adapter for Indian personal finance and investment communities.

Searches target subreddits (r/IndiaInvestments, r/mutualfunds, r/IndianStockMarket)
for first-time mutual fund and SIP discussions using PRAW, with graceful offline
fallback when credentials or network connectivity are unavailable.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import praw
from prawcore.exceptions import PrawcoreException

from src.connectors.base import BaseSourceConnector, RawRecord

logger = logging.getLogger("groww_discovery.connectors.reddit")

DEFAULT_SUBREDDITS = ["IndiaInvestments", "mutualfunds", "IndianStockMarket"]
DEFAULT_QUERIES = [
    "first sip",
    "sip review",
    "stop sip",
    "pause sip",
    "xirr confusion",
]


class RedditConnector(BaseSourceConnector):
    """Ingestion connector for Reddit submissions and comments."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.subreddits = self.config.get("subreddits", DEFAULT_SUBREDDITS)
        self.search_queries = self.config.get("search_queries", DEFAULT_QUERIES)
        self.limit_per_query = self.config.get("limit_per_query", 50)
        self.client_id = os.environ.get("REDDIT_CLIENT_ID") or self.config.get("client_id")
        self.client_secret = os.environ.get("REDDIT_CLIENT_SECRET") or self.config.get("client_secret")
        self.user_agent = (
            os.environ.get("REDDIT_USER_AGENT")
            or self.config.get("user_agent", "GrowwDiscoveryEngine/1.0 by GrowthEng")
        )

    def _init_reddit_client(self) -> Optional[praw.Reddit]:
        """Initialize PRAW client if credentials are configured."""
        if not self.client_id or not self.client_secret:
            logger.warning(
                "Reddit credentials not configured (REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET missing). "
                "Will attempt offline fallback or mock mode."
            )
            return None

        try:
            return praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                check_for_updates=False,
            )
        except Exception as e:
            logger.error("Failed to initialize PRAW client: %s", str(e))
            return None

    def fetch_records(
        self,
        subreddits: Optional[List[str]] = None,
        search_queries: Optional[List[str]] = None,
        limit_per_query: Optional[int] = None,
        fallback_file: Optional[Path] = None,
        **kwargs
    ) -> List[RawRecord]:
        """Harvest discussions across targeted personal finance subreddits.

        If Reddit API returns 401/403 or credentials are absent, falls back to
        the local curated dataset for offline reproducibility.
        """
        subs = subreddits or self.subreddits
        queries = search_queries or self.search_queries
        limit = limit_per_query or self.limit_per_query

        reddit = self._init_reddit_client()
        records: List[RawRecord] = []
        seen_ids = set()

        if reddit:
            try:
                for sub_name in subs:
                    logger.info("Searching subreddit 'r/%s'...", sub_name)
                    subreddit = reddit.subreddit(sub_name)

                    for query in queries:
                        try:
                            results = subreddit.search(query, sort="relevance", limit=limit)
                            for post in results:
                                if post.id in seen_ids:
                                    continue
                                seen_ids.add(post.id)

                                full_text = f"{post.title}\n{post.selftext}".strip()
                                if not full_text or len(full_text.split()) < 4:
                                    continue

                                pub_date = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                                author_name = post.author.name if post.author else None

                                is_groww = "groww" in full_text.lower()
                                product_context = "groww_specific" if is_groww else "category_level"

                                thread_ctx = {
                                    "parent_title": post.title,
                                    "subreddit": sub_name,
                                    "score": post.score,
                                    "num_comments": post.num_comments,
                                    "upvote_ratio": post.upvote_ratio,
                                    "search_query": query,
                                }

                                record = RawRecord(
                                    raw_id=f"reddit_submission_{post.id}",
                                    source_platform="reddit",
                                    source_url=f"https://www.reddit.com{post.permalink}",
                                    author_id_hash=self.hash_author(author_name),
                                    published_at=pub_date,
                                    collected_at=datetime.now(timezone.utc),
                                    raw_text=full_text,
                                    thread_context=thread_ctx,
                                    product_context=product_context,
                                )
                                records.append(record)
                        except PrawcoreException as pe:
                            logger.warning(
                                "Reddit API error for query '%s' in 'r/%s': %s",
                                query, sub_name, str(pe)
                            )
                            break  # Exit query loop on auth/rate-limit error
            except Exception as e:
                logger.error("Reddit ingestion failed with exception: %s", str(e), exc_info=True)

        # If live fetch yielded records, return them
        if records:
            logger.info("Harvested %d Reddit records from live API", len(records))
            return records

        # Otherwise, attempt offline fallback loading
        resolved_fallback = fallback_file or (
            Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "reddit_pilot_samples.json"
        )
        if resolved_fallback.exists():
            logger.info("Loading Reddit records from offline fallback file: %s", resolved_fallback)
            try:
                with open(resolved_fallback, "r", encoding="utf-8") as f:
                    samples = json.load(f)
                for item in samples:
                    records.append(RawRecord(**item))
                logger.info("Loaded %d records from fallback dataset", len(records))
                return records
            except Exception as e:
                logger.error("Failed to load Reddit fallback file: %s", str(e))

        logger.warning("No Reddit records harvested and no fallback data available.")
        return []
