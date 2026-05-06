"""
core/location.py
────────────────
Shared country/region detection used by all feeds.
Centralised so every source benefits from improvements.
"""

from typing import Optional

# Standard country list — extend freely
COUNTRIES = [
    "Nigeria", "Ukraine", "Russia", "Israel", "Palestine", "Gaza",
    "Sudan", "Syria", "Iraq", "Iran", "Afghanistan", "Pakistan",
    "Ethiopia", "Somalia", "Mali", "Libya", "Yemen", "Lebanon",
    "Myanmar", "Haiti", "Congo", "Kenya", "Egypt", "Turkey",
    "China", "Taiwan", "North Korea", "South Korea", "India",
    "Bangladesh", "France", "Germany", "United Kingdom", "USA",
    "Brazil", "Mexico", "Venezuela", "Colombia", "Serbia", "Kosovo",
    "Sahel", "West Africa", "East Africa", "Middle East",
    "Kashmir", "Donbas", "Nagorno-Karabakh",
]

# Alias map: fuzzy terms → canonical country name
ALIASES = {
    "kyiv":          "Ukraine",
    "moscow":        "Russia",
    "beijing":       "China",
    "tehran":        "Iran",
    "kabul":         "Afghanistan",
    "khartoum":      "Sudan",
    "damascus":      "Syria",
    "baghdad":       "Iraq",
    "sanaa":         "Yemen",
    "port-au-prince":"Haiti",
    "lagos":         "Nigeria",
    "abuja":         "Nigeria",
    "nairobi":       "Kenya",
    "tripoli":       "Libya",
    "beirut":        "Lebanon",
    "west bank":     "Palestine",
    "yangon":        "Myanmar",
}

# Keyword → category mapping
CONFLICT_KEYWORDS = {
    "conflict":  ["war",     "airstrike", "missile",  "shelling", "bombing",
                  "troops",  "military",  "soldiers",  "battle",   "front",
                  "attack",  "killed",    "casualties","strike",   "explosion"],
    "protest":   ["protest", "demonstrat","riot",      "march",    "rally",
                  "uprising","unrest",    "clashes",   "opposition"],
    "violence":  ["violence","gang",      "shooting",  "stabbing", "massacre",
                  "execution","armed group","militia"],
}


def detect_country(text: str) -> str:
    text_lower = text.lower()

    # Check aliases first (city names etc.)
    for alias, country in ALIASES.items():
        if alias in text_lower:
            return country

    # Then full country names
    for country in COUNTRIES:
        if country.lower() in text_lower:
            return country

    return "Unknown"


def detect_category(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in CONFLICT_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return "general"


def is_conflict_related(text: str) -> bool:
    all_keywords = [kw for kws in CONFLICT_KEYWORDS.values() for kw in kws]
    text_lower = text.lower()
    return any(kw in text_lower for kw in all_keywords)
