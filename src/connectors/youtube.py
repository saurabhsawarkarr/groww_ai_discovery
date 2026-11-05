"""YouTube comments ingestion adapter for Indian personal finance educational videos.

Uses YouTube Data API v3 to search SIP tutorial videos and harvest viewer comments,
capturing doubts, friction points, and mental models of first-time investors.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.connectors.base import BaseSourceConnector, RawRecord

logger = logging.getLogger("groww_discovery.connectors.youtube")

DEFAULT_YOUTUBE_QUERIES = [
    "first time mutual fund sip india",
    "how to choose sip groww",
    "sip xirr negative returns explained",
]


class YouTubeConnector(BaseSourceConnector):
    """Ingestion connector for YouTube video comments via YouTube Data API v3."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.queries = self.config.get("queries", DEFAULT_YOUTUBE_QUERIES)
        self.max_results = self.config.get("max_results", 50)
        self.api_key = os.environ.get("YOUTUBE_API_KEY") or self.config.get("api_key")

    def _init_client(self):
        """Initialize Google API client for YouTube Data API v3."""
        if not self.api_key:
            logger.warning("YouTube API Key not configured (YOUTUBE_API_KEY environment variable missing).")
            return None
        try:
            return build("youtube", "v3", developerKey=self.api_key)
        except Exception as e:
            logger.error("Failed to build YouTube service client: %s", str(e))
            return None

    def fetch_records(
        self,
        queries: Optional[List[str]] = None,
        max_videos_per_query: int = 3,
        max_comments_per_video: int = 25,
        fallback_file: Optional[Path] = None,
        **kwargs
    ) -> List[RawRecord]:
        """Harvest comments from top SIP educational videos on YouTube.

        If API key is missing or quota is exceeded, falls back gracefully to
        local curated dataset if available.
        """
        search_queries = queries or self.queries
        client = self._init_client()
        records: List[RawRecord] = []
        seen_comment_ids = set()

        if client:
            try:
                for query in search_queries:
                    logger.info("Searching YouTube videos for: '%s'", query)
                    search_response = client.search().list(
                        q=query,
                        part="id,snippet",
                        maxResults=max_videos_per_query,
                        type="video",
                        relevanceLanguage="en",
                    ).execute()

                    for item in search_response.get("items", []):
                        video_id = item["id"]["videoId"]
                        video_title = item["snippet"]["title"]

                        try:
                            comment_response = client.commentThreads().list(
                                part="snippet",
                                videoId=video_id,
                                maxResults=max_comments_per_video,
                                order="relevance",
                                textFormat="plainText",
                            ).execute()

                            for c_item in comment_response.get("items", []):
                                snippet = c_item["snippet"]["topLevelComment"]["snippet"]
                                comment_id = c_item["id"]

                                if comment_id in seen_comment_ids:
                                    continue
                                seen_comment_ids.add(comment_id)

                                text = (snippet.get("textDisplay") or "").strip()
                                if not text or len(text.split()) < 4:
                                    continue

                                pub_str = snippet.get("publishedAt")
                                pub_date = None
                                if pub_str:
                                    try:
                                        pub_date = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                                    except Exception:
                                        pub_date = datetime.now(timezone.utc)

                                is_groww = "groww" in text.lower() or "groww" in video_title.lower()
                                product_context = "groww_specific" if is_groww else "category_level"

                                thread_ctx = {
                                    "video_id": video_id,
                                    "video_title": video_title,
                                    "like_count": snippet.get("likeCount", 0),
                                    "total_reply_count": c_item["snippet"].get("totalReplyCount", 0),
                                    "search_query": query,
                                }

                                record = RawRecord(
                                    raw_id=f"youtube_comment_{comment_id}",
                                    source_platform="youtube",
                                    source_url=f"https://www.youtube.com/watch?v={video_id}&lc={comment_id}",
                                    author_id_hash=self.hash_author(snippet.get("authorDisplayName")),
                                    published_at=pub_date,
                                    collected_at=datetime.now(timezone.utc),
                                    raw_text=text,
                                    thread_context=thread_ctx,
                                    product_context=product_context,
                                )
                                records.append(record)
                        except HttpError as he:
                            logger.warning(
                                "Failed to fetch comments for video '%s': %s",
                                video_id, str(he)
                            )
            except Exception as e:
                logger.error("YouTube ingestion failed: %s", str(e), exc_info=True)

        if records:
            logger.info("Harvested %d YouTube comment records", len(records))
            return records

        # Fallback to local offline file
        resolved_fallback = fallback_file or (
            Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "youtube_pilot_samples.json"
        )
        if resolved_fallback.exists():
            logger.info("Loading YouTube records from offline fallback file: %s", resolved_fallback)
            try:
                with open(resolved_fallback, "r", encoding="utf-8") as f:
                    samples = json.load(f)
                for item in samples:
                    records.append(RawRecord(**item))
                logger.info("Loaded %d records from fallback dataset", len(records))
                return records
            except Exception as e:
                logger.error("Failed to load YouTube fallback file: %s", str(e))

        logger.warning("No YouTube records harvested and no fallback file available.")
        return []
