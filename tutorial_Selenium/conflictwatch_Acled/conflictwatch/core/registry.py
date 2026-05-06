"""
core/registry.py
────────────────
Central feed registry.
To add a new source: import it and call registry.register(MyFeed()).
The pipeline will pick it up automatically — nothing else changes.
"""

from typing import Dict, List, Type
from core.base_feed import BaseFeed, ConflictEvent
import logging

logger = logging.getLogger(__name__)


class FeedRegistry:
    def __init__(self):
        self._feeds: Dict[str, BaseFeed] = {}

    def register(self, feed: BaseFeed) -> None:
        self._feeds[feed.name] = feed
        logger.info(f"[registry] Registered feed: {feed.name}")

    def get(self, name: str) -> BaseFeed | None:
        return self._feeds.get(name)

    def all_available(self) -> List[BaseFeed]:
        return [f for f in self._feeds.values() if f.is_available()]

    def fetch_all(self) -> List[ConflictEvent]:
        """Fetch from every registered, available feed. Failures are logged, not raised."""
        events = []
        for feed in self.all_available():
            try:
                logger.info(f"[{feed.name}] Fetching...")
                result = feed.fetch()
                logger.info(f"[{feed.name}] Got {len(result)} events")
                events.extend(result)
            except Exception as e:
                logger.error(f"[{feed.name}] Failed: {e}")
        return events

    def status(self) -> dict:
        return {
            name: feed.is_available()
            for name, feed in self._feeds.items()
        }


# Singleton — import this everywhere
registry = FeedRegistry()
