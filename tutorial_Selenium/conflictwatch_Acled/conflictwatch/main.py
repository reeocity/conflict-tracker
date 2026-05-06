"""
main.py
───────
Entry point. Registers all feeds and runs the pipeline.

To add a new source:
  1. Create feeds/mysource.py extending BaseFeed
  2. Add one line below: registry.register(MySourceFeed())
  3. Done — the pipeline picks it up automatically.
"""

import logging
from core.registry import registry
from core.base_feed import ConflictEvent
from typing import List

# ─── Configure logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# ─── Register feeds ───────────────────────────────────────────────────────────
# ACTIVE
from feeds.aljazeera import AlJazeeraFeed
registry.register(AlJazeeraFeed())

# READY (flip is_available() in each file to activate)
from feeds.gdelt  import GDELTFeed
from feeds.acled  import ACLEDFeed
registry.register(GDELTFeed())
registry.register(ACLEDFeed())

# Future: just add more lines here
# from feeds.reuters    import ReutersFeed;  registry.register(ReutersFeed())
# from feeds.reliefweb  import ReliefWebFeed; registry.register(ReliefWebFeed())


# ─── Pipeline ────────────────────────────────────────────────────────────────
def run_pipeline() -> List[ConflictEvent]:
    print("\n" + "=" * 65)
    print("  CONFLICTWATCH — Multi-Source Intelligence Pipeline")
    print("=" * 65)

    # Show which sources are online
    status = registry.status()
    for name, available in status.items():
        icon = "✅" if available else "⏸️ "
        print(f"  {icon}  {name}")
    print()

    # Fetch from all available sources
    events = registry.fetch_all()

    # De-duplicate by URL
    seen_urls = set()
    unique = []
    for e in events:
        if e.url not in seen_urls:
            seen_urls.add(e.url)
            unique.append(e)   

    # Sort by date descending
    unique.sort(key=lambda e: e.date, reverse=True)

    # ─── Print results ────────────────────────────────────────────────────────
    print(f"{'─'*65}")
    print(f"  {len(unique)} events collected from {sum(v for v in status.values())} active source(s)")
    print(f"{'─'*65}\n")

    cat_icons = {"conflict": "💥", "protest": "✊", "violence": "⚠️", "general": "📰"}

    unknown_count = 0
    for i, event in enumerate(unique, 1):
        icon = cat_icons.get(event.category, "📰")
        country_display = event.country if event.country != "Unknown" else "❓ Unknown"
        if event.country == "Unknown":
            unknown_count += 1

        print(f"[{i:02d}] {icon}  [{country_display}]")
        print(f"      {event.title}")
        print(f"      📅 {event.date}  |  🏷  {event.category}  |  🔌 {event.source}")
        if event.description:
            desc = event.description[:120] + "..." if len(event.description) > 120 else event.description
            print(f"      📝 {desc}")
        print()

    # ─── Summary ─────────────────────────────────────────────────────────────
    print(f"{'─'*65}")
    print(f"  📊 SUMMARY")
    print(f"     Total events     : {len(unique)}")
    print(f"     Located          : {len(unique) - unknown_count}")
    print(f"     Unknown region   : {unknown_count}")

    categories = {}
    for e in unique:
        categories[e.category] = categories.get(e.category, 0) + 1
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"     {cat_icons.get(cat,'📰')} {cat:<12}: {count}")

    print(f"{'─'*65}\n")
    return unique


if __name__ == "__main__":
    run_pipeline()
