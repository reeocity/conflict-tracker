"""
feeds/aljazeera.py
──────────────────
Al Jazeera RSS feed — ACTIVE source.
Implements BaseFeed. Zero config required.
"""

import requests
import xml.etree.ElementTree as ET
import logging
from typing import List
from datetime import datetime

from core.base_feed import BaseFeed, ConflictEvent
from core.location import detect_country, detect_category, is_conflict_related

logger = logging.getLogger(__name__)

RSS_URL = "https://www.aljazeera.com/xml/rss/all.xml"
HEADERS = {"User-Agent": "Mozilla/5.0 (ConflictWatch/1.0)"}


class AlJazeeraFeed(BaseFeed):

    @property
    def name(self) -> str:
        return "aljazeera"

    def fetch(self) -> List[ConflictEvent]:
        try:
            response = requests.get(RSS_URL, headers=HEADERS, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)
        except Exception as e:
            logger.error(f"[aljazeera] Fetch failed: {e}")
            return []

        events = []
        for item in root.findall("./channel/item"):
            title       = (item.find("title").text       or "").strip()
            link        = (item.find("link").text        or "").strip()
            description = (item.find("description").text or "").strip()
            pub_date    = (item.find("pubDate").text     or "").strip()

            # Skip non-conflict content
            full_text = f"{title} {description}"
            if not is_conflict_related(full_text):
                continue

            # Detect country: title first, fall back to description
            country = detect_country(title)
            if country == "Unknown":
                country = detect_country(description)

            # Normalize date
            try:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                date_str = pub_date[:10] if pub_date else "Unknown"

            events.append(ConflictEvent(
                source      = self.name,
                title       = title,
                url         = link,
                date        = date_str,
                country     = country,
                region      = None,              # RSS doesn't give sub-regions
                category    = detect_category(full_text),
                description = description,
                raw         = {"pub_date": pub_date, "link": link},
            ))

        logger.info(f"[aljazeera] {len(events)} conflict events found")
        return events
