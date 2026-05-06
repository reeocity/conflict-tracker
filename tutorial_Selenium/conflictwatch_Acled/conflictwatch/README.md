# ConflictWatch — Modular Multi-Source Pipeline

## Architecture

```
conflictwatch/
├── core/
│   ├── base_feed.py     # Abstract interface every source must implement
│   ├── registry.py      # Central feed registry & fetch orchestrator
│   └── location.py      # Shared country/category detection (used by all feeds)
│
├── feeds/
│   ├── aljazeera.py     # ✅ ACTIVE  — Al Jazeera RSS (no config needed)
│   ├── gdelt.py         # ⏸️  READY   — flip is_available() to True to activate
│   └── acled.py         # ⏸️  READY   — set ACLED_EMAIL + ACLED_KEY env vars
│
├── main.py              # Entry point — registers feeds, runs pipeline
└── requirements.txt
```

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Adding a New Source

1. Create `feeds/mysource.py`:

```python
from core.base_feed import BaseFeed, ConflictEvent
from core.location import detect_country, detect_category

class MySourceFeed(BaseFeed):

    @property
    def name(self) -> str:
        return "mysource"

    def fetch(self) -> List[ConflictEvent]:
        # pull your data, return list of ConflictEvent
        ...
```

2. Register it in `main.py`:

```python
from feeds.mysource import MySourceFeed
registry.register(MySourceFeed())
```

That's it. The pipeline picks it up automatically.

## Activating GDELT (free, no key)

In `feeds/gdelt.py`, change:
```python
return False  # is_available()
```
to:
```python
return True
```

## Activating ACLED (requires free API key)

1. Register at https://developer.acleddata.com/
2. Set environment variables:
```bash
export ACLED_EMAIL="you@example.com"
export ACLED_KEY="your_key_here"
```
3. In `feeds/acled.py`, change `return False` to `return has_key`

## ConflictEvent — Unified Data Format

Every source outputs this same shape, regardless of where it came from:

| Field       | Type    | Description                        |
|-------------|---------|------------------------------------|
| source      | str     | "aljazeera", "gdelt", "acled"      |
| title       | str     | Headline                           |
| url         | str     | Link to original article           |
| date        | str     | ISO format: "2026-05-04"           |
| country     | str     | "Nigeria", "Ukraine", etc.         |
| region      | str     | Sub-region / city if available     |
| category    | str     | "conflict", "protest", "violence"  |
| description | str     | Summary / body text                |
| latitude    | float   | For map view (ACLED provides this) |
| longitude   | float   | For map view (ACLED provides this) |

## Design Principle

> The pipeline doesn't care where data comes from.
> It only speaks `ConflictEvent`.
> Adding a source = 1 file + 1 line in main.py.
