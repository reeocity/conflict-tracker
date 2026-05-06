"""
feeds/acled.py
──────────────
ACLED (Armed Conflict Location & Event Data) — STUB (requires API key).

ACLED is the gold standard for structured conflict data.
Covers 200+ countries, includes lat/lon, event type, fatalities.

To activate:
  1. Register at https://developer.acleddata.com/
  2. Set env vars:  ACLED_EMAIL and ACLED_KEY
  3. Flip is_available() to return True
  4. Uncomment ACLEDFeed in main.py registration block

Docs: https://developer.acleddata.com/rehd/cms_uploads/2023/07/ACLED_API-User-Guide_2023.pdf
"""

import os
import requests
import logging
from typing import List

from core.base_feed import BaseFeed, ConflictEvent

logger = logging.getLogger(__name__)

ACLED_BASE = "https://api.acleddata.com/acled/read"

# ACLED event types → our categories
EVENT_TYPE_MAP = {
    "Battles":                    "conflict",
    "Violence against civilians": "violence",
    "Explosions/Remote violence": "conflict",
    "Protests":                   "protest",
    "Riots":                      "protest",
    "Strategic developments":     "general",
}


class ACLEDFeed(BaseFeed):

    @property
    def name(self) -> str:
        return "acled"

    def is_available(self) -> bool:
        has_key = bool(os.getenv("ACLED_EMAIL") and os.getenv("ACLED_KEY"))
        if not has_key:
            logger.debug("[acled] ACLED_EMAIL / ACLED_KEY env vars not set")
        return False  # ← flip to has_key once you have credentials

    def fetch(self) -> List[ConflictEvent]:
        email = os.getenv("ACLED_EMAIL")
        key   = os.getenv("ACLED_KEY")

        params = {
            "email":   email,
            "key":     key,
            "limit":   100,
            "fields":  "event_date|country|location|latitude|longitude|event_type|notes|source_url",
        }

        try:
            response = requests.get(ACLED_BASE, params=params, timeout=15)
            response.raise_for_status()
            data = response.json().get("data", [])
        except Exception as e:
            logger.error(f"[acled] Fetch failed: {e}")
            return []

        events = []
        for row in data:
            event_type = row.get("event_type", "")
            category   = EVENT_TYPE_MAP.get(event_type, "general")
            country    = row.get("country", "Unknown")
            location   = row.get("location", "")

            events.append(ConflictEvent(
                source      = self.name,
                title       = f"[{country}] {event_type} in {location}",
                url         = row.get("source_url", ""),
                date        = row.get("event_date", ""),
                country     = country,
                region      = location,
                category    = category,
                description = row.get("notes", ""),
                latitude    = float(row["latitude"])  if row.get("latitude")  else None,
                longitude   = float(row["longitude"]) if row.get("longitude") else None,
                raw         = row,
            ))

        logger.info(f"[acled] {len(events)} events fetched")
        return events
