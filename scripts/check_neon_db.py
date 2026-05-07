#!/usr/bin/env python
"""
Check Neon DB for `events` table and row count.
"""
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print('DATABASE_URL not set in environment or .env')
    raise SystemExit(1)

import psycopg2
from urllib.parse import urlparse


def redact_database_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or "unknown-host"
    database = (parsed.path or "/").lstrip("/") or "unknown-db"
    return f"{parsed.scheme}://***:***@{host}/{database}"

print('Connecting to:', redact_database_url(DATABASE_URL))
conn = psycopg2.connect(DATABASE_URL)
try:
    with conn.cursor() as cur:
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = 'events';")
        rows = cur.fetchall()
        if not rows:
            print('\nNo table named "events" found in database.')
        else:
            print('\nFound table(s):')
            for schema, name in rows:
                print(f'  - {schema}.{name}')
            cur.execute('SELECT count(*) FROM public.events;')
            count = cur.fetchone()[0]
            print(f'\nRow count in public.events: {count}')
finally:
    conn.close()
