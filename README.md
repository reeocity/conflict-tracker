# Conflict Tracker — News Scraping & Alert System

A full-stack conflict monitoring web application that tracks global conflict-related events from news sources and delivers personalized alerts to users.

## 📋 Overview

The system collects news data from **Al Jazeera**, **GDELT**, and **ACLED**, filters for conflict-related events, and provides near real-time updates through a web interface and notification system.

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 20+** (for frontend if you use React)
- **PostgreSQL 12+** (for database)
- **Git**

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/reeocity/conflict-tracker.git
cd conflict-tracker
```

#### 2. Set up Python environment
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows PowerShell
source .venv/bin/activate          # macOS/Linux
```

#### 3. Install Python dependencies
```bash
pip install -U pip
pip install -r requirements.txt
```

#### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your values:
```bash
copy .env.example .env             # Windows
cp .env.example .env               # macOS/Linux
```

Edit `.env` with your database credentials:
```
DB_HOST=localhost
DB_NAME=conflict_news
DB_USER=postgres
DB_PASSWORD=your_secure_password
```

#### 5. (Optional) Set up PostgreSQL database
If you don't have a Postgres instance running:

**On Windows:**
```powershell
winget install --id PostgreSQL.PostgreSQL
```

**On macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**On Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

Then create the database:
```bash
psql -U postgres
CREATE DATABASE conflict_news;
\q
```

## 📁 Project Structure

```
tutorial_Selenium/
├── rss_scraper.py                # Simple Al Jazeera RSS scraper
├── sql.py                        # RSS scraper + Postgres saver
├── tutorial.py                   # Selenium example (headlines scraping)
├── main.py                       # FastAPI backend (sample data)
└── conflictwatch_Acled/          # Multi-source pipeline
    └── conflictwatch/
        ├── main.py               # Pipeline entry point
        ├── core/
        │   ├── base_feed.py      # Base class for all feeds
        │   ├── registry.py       # Feed registry (singleton)
        │   └── location.py       # Country/region detection
        └── feeds/
            ├── aljazeera.py      # Al Jazeera (active)
            ├── gdelt.py          # GDELT (stub, ready to activate)
            └── acled.py          # ACLED (stub, requires API key)
```

## 🎯 Running Scrapers

### 1. Simple RSS Scraper (No database)
Quick demo — prints conflict articles from Al Jazeera to console.

```bash
cd tutorial_Selenium
python rss_scraper.py
```

**Output:** Prints conflict articles with detected country/region.

---

### 2. Scraper + Database Saver
Scrapes Al Jazeera RSS and saves unique events to Postgres.

**Prerequisites:** PostgreSQL running and `.env` configured.

```bash
cd tutorial_Selenium
python sql.py
```

**Output:** Creates `events` table and prints saved/skipped articles.

---

### 3. Multi-Source Pipeline (Al Jazeera + GDELT + ACLED)
Unified pipeline that fetches from multiple sources, deduplicates, and prints results.

```bash
cd tutorial_Selenium/conflictwatch_Acled/conflictwatch
python main.py
```

**Active by default:** Al Jazeera  
**Available (disabled):** GDELT, ACLED

**To enable GDELT:**
- Edit `feeds/gdelt.py`, change `is_available()` to return `True`
- Re-run `main.py`

**To enable ACLED:**
- Set env vars: `ACLED_EMAIL` and `ACLED_KEY`
- Edit `feeds/acled.py`, change `is_available()` to return `has_key`
- Re-run `main.py`

---

## 🌐 Running FastAPI Backend

### Start the API server

```bash
cd tutorial_Selenium
python -m uvicorn main:app --reload --port 8000
```

**Server runs at:** `http://localhost:8000`  
**Docs:** `http://localhost:8000/docs` (Swagger UI)

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/news` | GET | Get all conflict events |
| `/api/news/{country}` | GET | Get events by country |
| `/api/stats` | GET | Get statistics (counts by category/country) |

**Example requests:**

```bash
# Get all news
curl http://localhost:8000/api/news

# Get news from Ukraine
curl http://localhost:8000/api/news/Ukraine

# Get stats
curl http://localhost:8000/api/stats
```

---

## 🧪 Testing

### Unit tests for location detection

```bash
pytest tutorial_Selenium/conflictwatch_Acled/conflictwatch/tests/ -v
```

(To be added in future commits)

---

## 🔧 Configuration

### Environment Variables

**Database:**
```
DB_HOST          → PostgreSQL host (default: localhost)
DB_NAME          → Database name (default: conflict_news)
DB_USER          → DB user (default: postgres)
DB_PASSWORD      → DB password (required)
```

**ACLED API (optional):**
```
ACLED_EMAIL      → Your ACLED account email
ACLED_KEY        → Your ACLED API key (get from https://developer.acleddata.com)
```

**FastAPI (optional):**
```
API_PORT         → Server port (default: 8000)
API_HOST         → Server host (default: 0.0.0.0)
```

---

## 📚 Architecture

### Data Collection Layer
- **Al Jazeera RSS:** Fetches latest articles in real-time via RSS feed
- **GDELT:** Free, massive world events database (updated every 15 min)
- **ACLED:** Curated conflict event data (requires API key)

### Processing Layer
- Filter articles by conflict-related keywords
- Detect country/region from title and description
- Categorize events (conflict, protest, violence)
- Remove duplicates by URL

### Storage
- **PostgreSQL:** Persistent event storage
- **Schema:** `events` table with title, link, date, region, etc.

### Backend API
- **FastAPI:** REST API serving event data
- **CORS enabled:** Frontend can query backend

---

## 🛣️ Roadmap

- [ ] Frontend React dashboard
- [ ] Real-time WebSocket notifications
- [ ] Email alert system (hourly summaries)
- [ ] User authentication & subscriptions
- [ ] Interactive map visualization
- [ ] Advanced NLP for event categorization
- [ ] Add more data sources (Reuters, BBC, etc.)
- [ ] Docker & Kubernetes deployment

---

## 🔐 Security Notes

**⚠️ Important:**
- Never commit `.env` or database credentials to version control
- Use `.env.example` as a template — never store actual secrets in the repo
- Run the app in a secure environment (use firewalls, VPNs)
- Validate all user input in production

---

## 🤝 Contributing

To contribute:

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Commit with clear messages: `git commit -m "feat: add new scraper"`
4. Push to your fork: `git push origin feature/my-feature`
5. Open a pull request

---

## 📞 Support

For issues, questions, or suggestions, open a GitHub issue or start a discussion.

---

## 📄 License

(Add your license here — e.g., MIT, GPL, etc.)
