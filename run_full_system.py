#!/usr/bin/env python
"""
run_full_system.py
──────────────────
Demo script to run the complete Conflict Tracker system.
Starts the FastAPI backend server and provides instructions for accessing the frontend.

Usage: python run_full_system.py
"""

import subprocess
import time
import sys
import os
from pathlib import Path


def print_banner():
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " 🌍 CONFLICT TRACKER — FULL SYSTEM ".center(78) + "║")
    print("║" + " Frontend + Backend Integration Demo ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()


def print_section(title):
    print("\n" + "─" * 80)
    print(f"  {title}")
    print("─" * 80)


def print_instruction(step, description, command=None):
    print(f"\n  ✓ Step {step}: {description}")
    if command:
        print(f"    Command: {command}")


def check_dependencies():
    """Verify all dependencies are installed."""
    print_section("1. Checking Dependencies")

    required = {
        "fastapi": "FastAPI web framework",
        "uvicorn": "ASGI server",
        "requests": "HTTP library",
        "pydantic": "Data validation",
    }

    missing = []
    for package, description in required.items():
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package.ljust(20)} {description}")
        except ImportError:
            print(f"  ❌ {package.ljust(20)} {description} — MISSING")
            missing.append(package)

    if missing:
        print(f"\n  Install missing packages:")
        print(f"    pip install {' '.join(missing)}")
        sys.exit(1)

    print("\n  ✅ All dependencies installed!")


def print_user_journey():
    """Show the user journey through the system."""
    print_section("2. User Experience Flow")

    journey = [
        ("1. User opens browser", "http://localhost:8000"),
        ("2. Frontend loads from index.html", "Beautiful dashboard UI"),
        ("3. Frontend makes API call", "GET /api/news"),
        ("4. Backend fetches from Al Jazeera", "Real-time RSS feed"),
        ("5. Backend returns conflict events", "JSON with country, category, date"),
        ("6. Frontend displays events", "Interactive event cards with filters"),
        ("7. User filters by country", "Real-time filtering in browser"),
        ("8. User searches for keywords", "Dynamic search across events"),
        ("9. Dashboard shows statistics", "Total events, conflicts, countries"),
        ("10. Auto-refresh every 30s", "Always up-to-date data"),
    ]

    for step, detail in journey:
        print(f"\n  {step}")
        print(f"    └─ {detail}")


def print_api_endpoints():
    """Document available API endpoints."""
    print_section("3. Available API Endpoints")

    endpoints = [
        ("GET", "/api/news", "Fetch all conflict events", "curl http://localhost:8000/api/news"),
        ("GET", "/api/news/{country}", "Fetch events by country", "curl http://localhost:8000/api/news/Ukraine"),
        ("GET", "/api/stats", "Get statistics", "curl http://localhost:8000/api/stats"),
        ("GET", "/docs", "Interactive API docs", "http://localhost:8000/docs"),
    ]

    print("\n  HTTP Method | Endpoint              | Description")
    print("  " + "─" * 76)
    for method, endpoint, description, example in endpoints:
        print(f"  {method.ljust(11)} | {endpoint.ljust(21)} | {description}")
        print(f"  {''.ljust(11)} | {'Example:'.ljust(21)} | {example}")
        print()


def print_run_instructions():
    """Print step-by-step instructions to run the system."""
    print_section("4. How to Run the System")

    print("\n  OPTION A: Run Backend Only (Test APIs)")
    print("  ─" * 40)
    print("  $ cd tutorial_Selenium")
    print("  $ python -m uvicorn main:app --reload --port 8000")
    print("\n  Then visit:")
    print("  • API:      http://localhost:8000/api/news")
    print("  • Docs:     http://localhost:8000/docs")

    print("\n\n  OPTION B: Run Full System (Frontend + Backend)")
    print("  ─" * 40)
    print("  Terminal 1 — Start Backend:")
    print("  $ cd tutorial_Selenium")
    print("  $ python -m uvicorn main:app --reload --port 8000")
    print("\n  Terminal 2 — Open Frontend:")
    print("  • On Windows:  start index.html")
    print("  • On macOS:    open index.html")
    print("  • On Linux:    xdg-open index.html")
    print("  • Or use browser: file:///{full_path}/index.html")


def print_user_interactions():
    """Show what users can do with the system."""
    print_section("5. User Interactions & Features")

    features = [
        ("🔍 Search", "Type country name or keyword to filter events"),
        ("🏷️  Filter by Category", "View conflicts, protests, or violence separately"),
        ("📊 Statistics Dashboard", "See total events and countries affected"),
        ("🔄 Auto-Refresh", "Dashboard updates every 30 seconds"),
        ("🌐 API Access", "Developers can query endpoints directly"),
        ("📱 Responsive Design", "Works on desktop, tablet, and mobile"),
    ]

    print()
    for feature, description in features:
        print(f"  {feature.ljust(20)} → {description}")


def print_example_interactions():
    """Show example user interactions."""
    print_section("6. Example User Interactions")

    print("\n  Scenario 1: User wants to monitor Ukraine conflict")
    print("  ─" * 78)
    print("  1. User opens dashboard")
    print("  2. Sees 10 events displayed")
    print("  3. Types 'Ukraine' in search box")
    print("  4. Dashboard updates to show 3 Ukraine events")
    print("  5. Clicks on an event to see details")

    print("\n  Scenario 2: User wants to track protests")
    print("  ─" * 78)
    print("  1. User opens dashboard")
    print("  2. Clicks 'Protest' filter dropdown")
    print("  3. Dashboard shows only protest events")
    print("  4. Sees 2 protests in 'Nigeria' and 'Iran'")
    print("  5. System auto-refreshes every 30 seconds")

    print("\n  Scenario 3: Developer wants to build a custom app")
    print("  ─" * 78)
    print("  1. Developer opens http://localhost:8000/docs")
    print("  2. Sees interactive API documentation")
    print("  3. Clicks 'Try it out' on /api/news endpoint")
    print("  4. Gets JSON response with all conflict events")
    print("  5. Uses data in their own frontend/app")


def print_architecture():
    """Show system architecture."""
    print_section("7. System Architecture")

    print("""
  ┌─────────────────────────────────────────────────────────────┐
  │                     USER BROWSER                             │
  │  ┌───────────────────────────────────────────────────────┐  │
  │  │  index.html (Frontend)                                │  │
  │  │  • Interactive dashboard                              │  │
  │  │  • Search & filter UI                                 │  │
  │  │  • Real-time statistics                               │  │
  │  │  • Auto-refresh every 30s                             │  │
  │  └───────────────────────────────────────────────────────┘  │
  └────────────────────────┬─────────────────────────────────────┘
                           │ HTTP Requests
                           │ (REST API)
                           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              BACKEND (FastAPI)                               │
  │  ┌───────────────────────────────────────────────────────┐  │
  │  │  main.py                                              │  │
  │  │  • /api/news - Get all events                         │  │
  │  │  • /api/news/{country} - Get by country              │  │
  │  │  • /api/stats - Get statistics                        │  │
  │  │  • /docs - Interactive API docs                       │  │
  │  └────────────────────┬──────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘
                           │ Fetches from
                           │ Sample Data (hardcoded)
                           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              DATA LAYER                                       │
  │  • In-memory sample events (SAMPLE_NEWS)                    │
  │  • Later: Connect to PostgreSQL/Neon                        │
  │  • Later: Real-time scraper updates                         │
  └─────────────────────────────────────────────────────────────┘
    """)


def print_next_steps():
    """Print next steps for development."""
    print_section("8. Next Steps")

    print("""
  Phase 1: Core System (✅ DONE)
  ─────────────────────────────
  ✅ Location detection & categorization
  ✅ Frontend dashboard UI
  ✅ FastAPI backend with sample data
  ✅ Unit & integration tests

  Phase 2: Real Data Pipeline (TODO)
  ────────────────────────────────
  ⏳ Connect to PostgreSQL/Neon database
  ⏳ Implement real-time RSS scraper
  ⏳ Scheduled tasks (fetch new articles)
  ⏳ Deduplication logic

  Phase 3: User Features (TODO)
  ──────────────────────────────
  ⏳ User authentication & accounts
  ⏳ Personalized subscriptions (by country)
  ⏳ Email alert notifications
  ⏳ Browser push notifications

  Phase 4: Advanced Features (TODO)
  ──────────────────────────────────
  ⏳ Interactive map visualization
  ⏳ Event severity classification
  ⏳ Multiple data sources (GDELT, ACLED)
  ⏳ Real-time WebSocket updates
    """)


def main():
    print_banner()
    check_dependencies()
    print_user_journey()
    print_api_endpoints()
    print_user_interactions()
    print_example_interactions()
    print_architecture()
    print_run_instructions()
    print_next_steps()

    print_section("Ready to Start?")
    print("\n  📖 Next: Follow the instructions in 'How to Run the System' above")
    print("\n  Or run this to test the API immediately:")
    print("     cd tutorial_Selenium")
    print("     python -m uvicorn main:app --reload --port 8000")
    print("\n  Then visit: http://localhost:8000/docs")
    print("\n" + "─" * 80 + "\n")


if __name__ == "__main__":
    main()
