"""
core/base_feed.py
─────────────────
Abstract base class every data source must implement.
Adding GDELT, ACLED, or any new source = subclass this + register it.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ConflictEvent:
    """
    Unified event format shared across ALL sources.
    No matter where data comes from, it ends up as this.
    """
    source:      str              # e.g. "aljazeera", "gdelt", "acled"
    title:       str
    url:         str
    date:        str              # ISO format: "2026-05-04"
    country:     str              # "Nigeria", "Ukraine", etc.
    region:      Optional[str]    # sub-region if available
    category:    str              # "conflict", "protest", "violence"
    description: Optional[str]   = None
    latitude:    Optional[float]  = None   # for map support later
    longitude:   Optional[float]  = None
    raw:         Optional[dict]   = field(default=None, repr=False)  # original data


class BaseFeed(ABC):
    """
    Every data source (Al Jazeera, GDELT, ACLED...) extends this.
    Only two methods required: name and fetch().
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier e.g. 'aljazeera', 'gdelt'"""
        ...

    @abstractmethod
    def fetch(self) -> List[ConflictEvent]:
        """Pull and return a list of ConflictEvents. Never raises — returns [] on failure."""
        ...

    def is_available(self) -> bool:
        """Override to add availability checks (API key present, etc.)"""
        return True
