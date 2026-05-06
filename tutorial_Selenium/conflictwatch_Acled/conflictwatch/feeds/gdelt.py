"""
feeds/gdelt.py
──────────────
GDELT Project feed — STUB (ready to activate).

GDELT is a free, massive database of world events updated every 15 minutes.
No API key needed — uses their public CSV endpoint.

To activate:
  1. Uncomment GDELTFeed in main.py registration block
  2. No other changes required

Docs: https://www.gdeltproject.org/data.html
"""

import requests
import csv
import io
import logging
from typing import List
from datetime import datetime

from core.base_feed import BaseFeed, ConflictEvent
from core.location import detect_country, detect_category

logger = logging.getLogger(__name__)

# GDELT last 15 minutes event CSV
GDELT_URL = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

# GDELT event codes that map to conflict/protest/violence
CONFLICT_EVENT_CODES = {
    "14":  "protest",    # Protest
    "145": "protest",    # Hunger strike
    "18":  "conflict",   # Assault
    "19":  "conflict",   # Fight
    "190": "conflict",   # Use unconventional mass violence
    "193": "conflict",   # Bomb/explode
    "195": "violence",   # Assassinate
    "20":  "conflict",   # Engage in unconventional mass violence
}


class GDELTFeed(BaseFeed):

    @property
    def name(self) -> str:
        return "gdelt"

    def is_available(self) -> bool:
        # GDELT is always available — no key needed
        # Set to False to disable without removing registration
        return False  # ← flip to True to activate

    def fetch(self) -> List[ConflictEvent]:
        try:
            # Step 1: Get the latest file list
            manifest = requests.get(GDELT_URL, timeout=10).text
            csv_url = None
            for line in manifest.splitlines():
                if "export.CSV" in line:
                    csv_url = line.split()[-1]
                    break

            if not csv_url:
                logger.error("[gdelt] Could not find CSV URL in manifest")
                return []

            # Step 2: Download and parse the CSV
            response = requests.get(csv_url, timeout=30)
            reader   = csv.reader(io.StringIO(response.text), delimiter="\t")

            events = []
            for row in reader:
                if len(row) < 60:
                    continue

                event_code   = row[28]        # EventBaseCode
                country_code = row[51]        # ActionGeo_CountryCode
                actor1       = row[6]         # Actor1Name
                date_str     = row[1][:8]     # YYYYMMDD
                url          = row[-1].strip()

                # Filter to conflict-related events only
                if not any(event_code.startswith(c) for c in CONFLICT_EVENT_CODES):
                    continue

                # Normalize date
                try:
                    dt = datetime.strptime(date_str, "%Y%m%d")
                    formatted_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    formatted_date = date_str

                country = detect_country(actor1) if actor1 else "Unknown"
                category = next(
                    (v for k, v in CONFLICT_EVENT_CODES.items() if event_code.startswith(k)),
                    "conflict"
                )

                events.append(ConflictEvent(
                    source   = self.name,
                    title    = f"[GDELT] {actor1 or 'Unknown actor'} — event {event_code}",
                    url      = url,
                    date     = formatted_date,
                    country  = country,
                    region   = country_code,
                    category = category,
                    raw      = {"event_code": event_code, "country_code": country_code},
                ))

            logger.info(f"[gdelt] {len(events)} events parsed")
            return events

        except Exception as e:
            logger.error(f"[gdelt] Error: {e}")
            return []
