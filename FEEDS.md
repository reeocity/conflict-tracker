# Activating Additional Data Feeds

This project supports multiple conflict data sources. **Al Jazeera is active by default.** Here's how to enable additional feeds.

## GDELT Feed (Free, No API Key Required)

GDELT is a massive, free database of world events updated every 15 minutes.

### To activate:

1. Open `tutorial_Selenium/conflictwatch_Acled/conflictwatch/feeds/gdelt.py`
2. Find the `is_available()` method (around line 40)
3. Change:
   ```python
   return False  # ← flip to True to activate
   ```
   To:
   ```python
   return True
   ```
4. Save and re-run the pipeline:
   ```bash
   cd tutorial_Selenium/conflictwatch_Acled/conflictwatch
   python main.py
   ```

**That's it!** GDELT events will now be fetched alongside Al Jazeera.

---

## ACLED Feed (Requires API Key)

ACLED (Armed Conflict Location & Event Data) is the gold standard for structured conflict data covering 200+ countries with precise lat/lon and event severity.

### Prerequisites:

- Register for a free account at: https://developer.acleddata.com/
- Request API access (usually instant)
- Get your email and API key

### To activate:

1. **Set environment variables** in your `.env` file:
   ```
   ACLED_EMAIL=your_email@example.com
   ACLED_KEY=your_acled_api_key_here
   ```

2. Open `tutorial_Selenium/conflictwatch_Acled/conflictwatch/feeds/acled.py`

3. Find the `is_available()` method (around line 45)

4. Change:
   ```python
   return False  # ← flip to has_key once you have credentials
   ```
   To:
   ```python
   return has_key
   ```
   
   (The `has_key` variable already checks if both env vars are set)

5. Save and re-run:
   ```bash
   cd tutorial_Selenium/conflictwatch_Acled/conflictwatch
   python main.py
   ```

**You'll now see ACLED events in the pipeline output.**

---

## Verifying Feeds Are Active

When you run the pipeline, you'll see a status dashboard:

```
═════════════════════════════════════════════════════════════
  CONFLICTWATCH — Multi-Source Intelligence Pipeline
═════════════════════════════════════════════════════════════
  ✅  aljazeera
  ✅  gdelt        (only if enabled)
  ✅  acled        (only if ACLED_EMAIL + ACLED_KEY set)
```

If a feed shows `⏸️` (paused icon) instead of `✅`, it's disabled.

---

## Adding Your Own Feed

To add a new data source (e.g., Reuters, BBC, etc.):

1. Create a new file: `tutorial_Selenium/conflictwatch_Acled/conflictwatch/feeds/mysource.py`

2. Extend `BaseFeed`:
   ```python
   from core.base_feed import BaseFeed, ConflictEvent
   
   class MySourceFeed(BaseFeed):
       @property
       def name(self) -> str:
           return "mysource"
       
       def fetch(self) -> List[ConflictEvent]:
           # Your scraping logic here
           events = [...]
           return events
   ```

3. Register it in `main.py`:
   ```python
   from feeds.mysource import MySourceFeed
   registry.register(MySourceFeed())
   ```

4. Run the pipeline — your feed will be auto-detected!

---

## Troubleshooting

**Feed shows `⏸️` (disabled)?**
- Check if required env vars are set: `printenv ACLED_EMAIL`
- Verify `is_available()` returns `True` in the feed file
- Check logs for error messages

**Feed returns no events?**
- Verify network connectivity: `curl https://www.aljazeera.com/xml/rss/all.xml` (for Al Jazeera)
- Check if the API endpoint is still valid (feeds may change URLs)
- Look for error messages in console output

**API rate limits hit?**
- GDELT: No rate limits (public data)
- ACLED: Free tier has limits; upgrade plan if needed
- Add delays between requests if needed: `time.sleep(1)`

---

For more details, see the main README.md.
