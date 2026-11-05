"""Multi-source ingestion adapters for Groww AI-Powered Discovery Engine."""

from src.connectors.base import BaseSourceConnector, RawRecord
from src.connectors.play_store import PlayStoreConnector
from src.connectors.app_store import AppStoreConnector
from src.connectors.reddit import RedditConnector
from src.connectors.youtube import YouTubeConnector
from src.connectors.file_importer import FileImporterConnector

__all__ = [
    "BaseSourceConnector",
    "RawRecord",
    "PlayStoreConnector",
    "AppStoreConnector",
    "RedditConnector",
    "YouTubeConnector",
    "FileImporterConnector",
]
