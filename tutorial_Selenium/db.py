import os
from datetime import datetime
from typing import Iterable, List, Optional

import psycopg2
from dotenv import load_dotenv


load_dotenv()


COUNTRY_ALIASES = {
    "kyiv": "Ukraine",
    "kiev": "Ukraine",
    "lagos": "Nigeria",
    "darfur": "Sudan",
    "gaza": "Gaza",
    "sagaing": "Myanmar",
    "port-au-prince": "Haiti",
    "amhara": "Ethiopia",
    "houthi": "Yemen",
    "cauca": "Colombia",
}

COUNTRIES = [
    "Nigeria", "Ukraine", "Russia", "Israel", "Palestine", "Gaza",
    "Sudan", "Syria", "Iraq", "Iran", "Afghanistan", "Pakistan",
    "Ethiopia", "Somalia", "Mali", "Libya", "Yemen", "Lebanon",
    "Myanmar", "Haiti", "Congo", "Kenya", "Egypt", "Turkey",
    "China", "Taiwan", "North Korea", "South Korea", "India",
    "Bangladesh", "France", "Germany", "UK", "USA", "Brazil",
    "Mexico", "Venezuela", "Colombia", "Serbia", "Kosovo"
]

CATEGORY_KEYWORDS = {
    "conflict": ["war", "attack", "airstrike", "clash", "strike", "assault", "bomb", "military"],
    "protest": ["protest", "demonstration", "rally", "march", "strike"],
    "violence": ["violence", "kill", "killed", "dead", "fatal", "gang"],
}


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    if all([host, database, user, password]):
        port = os.getenv("DB_PORT", "5432")
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    raise RuntimeError("DATABASE_URL or DB_* environment variables must be set")


def connect_db():
    return psycopg2.connect(get_database_url())


def setup_db(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT UNIQUE,
                date TEXT,
                country TEXT,
                region TEXT,
                category TEXT,
                description TEXT,
                scraped_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS events_country_idx ON events (country);")
        cur.execute("CREATE INDEX IF NOT EXISTS events_category_idx ON events (category);")
        conn.commit()


def setup_auth_db(conn):
    """Create user authentication tables"""
    with conn.cursor() as cur:
        # Users table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS users_email_idx ON users (email);")
        
        # User alert subscriptions table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_alert_subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                country VARCHAR(100),
                category VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS subs_user_idx ON user_alert_subscriptions (user_id);")
        conn.commit()


def detect_country(text: str) -> str:
    text_lower = (text or "").lower()
    for alias, country in COUNTRY_ALIASES.items():
        if alias in text_lower:
            return country
    for country in COUNTRIES:
        if country.lower() in text_lower:
            return country
    return "Unknown"


def detect_category(text: str) -> str:
    text_lower = (text or "").lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "general"


def save_event(conn, title: str, link: str, date: str, country: str, region: str, category: str, description: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO events (title, link, date, country, region, category, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (link) DO UPDATE SET
                title = EXCLUDED.title,
                date = EXCLUDED.date,
                country = EXCLUDED.country,
                region = EXCLUDED.region,
                category = EXCLUDED.category,
                description = EXCLUDED.description,
                scraped_at = NOW();
            """,
            (title, link, date, country, region, category, description),
        )
        conn.commit()


def fetch_events(conn, country: Optional[str] = None):
    with conn.cursor() as cur:
        if country:
            cur.execute(
                """
                SELECT id, country, title, date, category
                FROM events
                WHERE LOWER(country) = LOWER(%s)
                ORDER BY scraped_at DESC, id DESC;
                """,
                (country,),
            )
        else:
            cur.execute(
                """
                SELECT id, country, title, date, category
                FROM events
                ORDER BY scraped_at DESC, id DESC;
                """
            )
        return cur.fetchall()


def fetch_stats(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM events;")
        total = cur.fetchone()[0]
        cur.execute("SELECT category, COUNT(*) FROM events GROUP BY category;")
        by_category = {row[0] or "general": row[1] for row in cur.fetchall()}
        cur.execute("SELECT country, COUNT(*) FROM events GROUP BY country;")
        by_country = {row[0] or "Unknown": row[1] for row in cur.fetchall()}
        return total, by_category, by_country
