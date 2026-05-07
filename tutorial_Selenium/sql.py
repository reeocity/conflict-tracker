import requests
import xml.etree.ElementTree as ET

from db import connect_db, detect_category, detect_country, save_event, setup_db


KEYWORDS = ["war", "attack", "protest", "violence", "conflict", "strike", "killed", "clash", "airstrike", "military"]


def scrape_and_save():
    conn = connect_db()
    setup_db(conn)

    url = "https://www.aljazeera.com/xml/rss/all.xml"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    print("=" * 60)
    print("AL JAZEERA — CONFLICT NEWS")
    print("=" * 60)

    count = 0
    saved = 0

    for item in root.findall("./channel/item"):
        title = item.findtext("title", default="")
        link = item.findtext("link", default="")
        date = item.findtext("pubDate", default="No date")
        description = item.findtext("description", default="")

        text_for_filter = f"{title} {description}".lower()
        if not any(keyword in text_for_filter for keyword in KEYWORDS):
            continue

        country = detect_country(title)
        if country == "Unknown":
            country = detect_country(description)

        region = country
        category = detect_category(f"{title} {description}")

        save_event(conn, title, link, date, country, region, category, description)
        count += 1
        saved += 1

        print(f"\n[{count}] ✅ Saved/updated")
        print(f"  Country: {country}")
        print(f"  Title  : {title}")
        print(f"  Link   : {link}")
        print(f"  Date   : {date}")
        print(f"  Category: {category}")
        print("-" * 60)

    print(f"\n📊 SUMMARY")
    print(f"  Total saved/updated : {saved}")
    print(f"  Records in this run  : {count}")

    conn.close()


if __name__ == "__main__":
    scrape_and_save()