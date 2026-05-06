import requests
import xml.etree.ElementTree as ET

# ─── STEP 1: Country List (Standard Format) ──────────────────────────────────
COUNTRIES = [
    "Nigeria", "Ukraine", "Russia", "Israel", "Palestine", "Gaza",
    "Sudan", "Syria", "Iraq", "Iran", "Afghanistan", "Pakistan",
    "Ethiopia", "Somalia", "Mali", "Libya", "Yemen", "Lebanon",
    "Myanmar", "Haiti", "Congo", "Kenya", "Egypt", "Turkey",
    "China", "Taiwan", "North Korea", "South Korea", "India",
    "Bangladesh", "France", "Germany", "UK", "USA", "Brazil",
    "Mexico", "Venezuela", "Colombia", "Serbia", "Kosovo"
]

# ─── STEP 2: Location Detector ───────────────────────────────────────────────
def detect_location(text):
    for country in COUNTRIES:
        if country.lower() in text.lower():
            return country
    return "Unknown Region"

# ─── STEP 3: Scrape Al Jazeera RSS ───────────────────────────────────────────
url = "https://www.aljazeera.com/xml/rss/all.xml"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
root = ET.fromstring(response.content)

# ─── STEP 4: Conflict Keywords Filter ────────────────────────────────────────
KEYWORDS = ["war", "attack", "protest", "violence", "conflict", "strike", "killed"]

print("=" * 60)
print("AL JAZEERA — CONFLICT NEWS WITH LOCATION")
print("=" * 60)

count = 0
unknown_count = 0

for item in root.findall("./channel/item"):
    title       = item.find("title").text or ""
    link        = item.find("link").text or ""
    date        = item.find("pubDate").text or "No date"
    description = item.find("description").text or ""  # article body/summary

    # Check for conflict keywords
    if any(keyword in title.lower() for keyword in KEYWORDS):

        # Detect location from title first, then description as fallback
        region = detect_location(title)
        if region == "Unknown Region":
            region = detect_location(description)

        count += 1
        if region == "Unknown Region":
            unknown_count += 1

        print(f"\n[{count}]")
        print(f"  Title  : {title}")
        print(f"  Link   : {link}")
        print(f"  Date   : {date}")
        print(f"  Region : {region}")
        print("-" * 60)

# ─── STEP 5: Summary ─────────────────────────────────────────────────────────
print(f"\nTotal conflict articles : {count}")
print(f"Located successfully    : {count - unknown_count}")
print(f"Unknown region          : {unknown_count}")