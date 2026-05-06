from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from pydantic import BaseModel
import os

app = FastAPI(title="Conflict News API")

# ─── CORS (allow React frontend to talk to backend) ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Mount static files ───────────────────────────────────────────────────────
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# ─── Data Model ───────────────────────────────────────────────────────────────
class NewsItem(BaseModel):
    id: int
    country: str
    headline: str
    date: str
    category: str

# ─── Sample Data ──────────────────────────────────────────────────────────────
SAMPLE_NEWS: List[NewsItem] = [
    NewsItem(id=1, country="Ukraine",     headline="Explosion reported in Kyiv near government district",       date="2026-05-04", category="conflict"),
    NewsItem(id=2, country="Nigeria",     headline="Protest in Lagos over fuel subsidy removal turns violent",  date="2026-05-04", category="protest"),
    NewsItem(id=3, country="Sudan",       headline="Armed attack on refugee camp kills dozens in Darfur",       date="2026-05-03", category="conflict"),
    NewsItem(id=4, country="Gaza",        headline="Airstrikes hit residential area overnight",                 date="2026-05-04", category="conflict"),
    NewsItem(id=5, country="Myanmar",     headline="Military strikes villages in Sagaing region",              date="2026-05-03", category="conflict"),
    NewsItem(id=6, country="Haiti",       headline="Gang violence forces thousands to flee Port-au-Prince",    date="2026-05-02", category="violence"),
    NewsItem(id=7, country="Ethiopia",    headline="Clashes resume in Amhara region despite ceasefire",        date="2026-05-04", category="conflict"),
    NewsItem(id=8, country="Yemen",       headline="Coalition airstrike targets Houthi weapons depot",         date="2026-05-03", category="conflict"),
    NewsItem(id=9, country="Iran",        headline="Protest spreads to five cities after student crackdown",   date="2026-05-04", category="protest"),
    NewsItem(id=10, country="Colombia",   headline="Armed group attacks military convoy in Cauca",             date="2026-05-02", category="conflict"),
]

# ─── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    frontend = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend)

@app.get("/api/news", response_model=List[NewsItem])
def get_news():
    return SAMPLE_NEWS

@app.get("/api/news/{country}")
def get_news_by_country(country: str):
    results = [n for n in SAMPLE_NEWS if n.country.lower() == country.lower()]
    return results

@app.get("/api/stats")
def get_stats():
    categories = {}
    countries = {}
    for item in SAMPLE_NEWS:
        categories[item.category] = categories.get(item.category, 0) + 1
        countries[item.country]   = countries.get(item.country, 0) + 1
    return {
        "total": len(SAMPLE_NEWS),
        "by_category": categories,
        "by_country": countries
    }
