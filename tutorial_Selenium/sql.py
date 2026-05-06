import requests
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2 import sql
from datetime import datetime

# ─── STEP 1: Database Connection ─────────────────────────────────────────────
def connect_db():
    return psycopg2.connect(
        host     = "localhost",
        database = "conflict_news",
        user     = "postgres",
        password = "YOUR_PASSWORD_HERE"  # ← change this
    )

# ─── STEP 2: Create Table If It Doesn't Exist ────────────────────────────────
def setup_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id        SERIAL PRIMARY KEY,
                title     TEXT NOT NULL,
                link      TEXT UNIQUE,       -- prevents duplicates
                date      TEXT,
                region    TEXT,
                scraped_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
    print("✅ Database ready")

# ─── STEP 3: Save Event to DB ────────────────────────────────────────────────
def save_event(conn, title, link, date, region):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO events (title, link, date, region)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (link) DO NOTHING;  -- skip if already saved
        """, (title, link, date, region))
        conn.commit()

# ─── STEP 4: Country List ────────────────────────────────────────────────────
COUNTRIES = [
    "Nigeria", "Ukraine", "Russia", "Israel", "Palestine", "Gaza",
    "Sudan", "Syria", "Iraq", "Iran", "Afghanistan", "Pakistan",
    "Ethiopia", "Somalia", "Mali", "Libya", "Yemen", "Lebanon",
    "Myanmar", "Haiti", "Congo", "Kenya", "Egypt", "Turkey",
    "China", "Taiwan", "North Korea", "South Korea", "India",
    "Bangladesh", "France", "Germany", "UK", "USA", "Brazil",
    "Mexico", "Venezuela", "Colombia", "Serbia", "Kosovo"
]

# ─── STEP 5: Location Detector ───────────────────────────────────────────────
def detect_location(text):
    for country in COUNTRIES:
        if country.lower() in text.lower():
            return country
    return "Unknown Region"

# ─── STEP 6: Scrape + Filter + Save ─────────────────────────────────────────
KEYWORDS = ["war", "attack", "protest", "violence", "conflict", "strike", "killed"]

def scrape_and_save():
    conn = connect_db()
    setup_db(conn)

    url = "https://www.aljazeera.com/xml/rss/all.xml"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    root = ET.fromstring(response.content)

    print("=" * 60)
    print("AL JAZEERA — CONFLICT NEWS")
    print("=" * 60)

    count       = 0
    saved       = 0
    skipped     = 0

    for item in root.findall("./channel/item"):
        title       = item.find("title").text or ""
        link        = item.find("link").text or ""
        date        = item.find("pubDate").text or "No date"
        description = item.find("description").text or ""

        if any(keyword in title.lower() for keyword in KEYWORDS):
            region = detect_location(title)
            if region == "Unknown Region":
                region = detect_location(description)

            count += 1

            # Check if already in DB
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM events WHERE link = %s", (link,))
                exists = cur.fetchone()

            if exists:
                skipped += 1
                status = "⚠️  Already in DB"
            else:
                save_event(conn, title, link, date, region)
                saved += 1
                status = "✅ Saved"

            print(f"\n[{count}] {status}")
            print(f"  Title  : {title}")
            print(f"  Link   : {link}")
            print(f"  Date   : {date}")
            print(f"  Region : {region}")
            print("-" * 60)

    # ─── Summary ─────────────────────────────────────────────────────────────
    print(f"\n📊 SUMMARY")
    print(f"  Total found : {count}")
    print(f"  Saved to DB : {saved}")
    print(f"  Duplicates  : {skipped}")

    conn.close()

# ─── RUN ─────────────────────────────────────────────────────────────────────
scrape_and_save()