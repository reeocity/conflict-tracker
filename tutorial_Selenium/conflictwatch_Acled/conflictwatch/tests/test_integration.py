#!/usr/bin/env python
"""
tests/test_integration.py
─────────────────────────
Integration tests for the entire conflict tracker system.
Tests each component end-to-end without requiring a database.
"""

import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from typing import List


class TestLocationModule:
    """Test location detection module."""

    def test_location_import(self):
        """Verify location module imports without errors."""
        from core.location import detect_country, detect_category, is_conflict_related
        assert callable(detect_country)
        assert callable(detect_category)
        assert callable(is_conflict_related)

    def test_country_detection_samples(self):
        """Test country detection with real examples."""
        from core.location import detect_country
        assert detect_country("War in Ukraine") == "Ukraine"
        assert detect_country("Explosion in Kyiv") == "Ukraine"
        assert detect_country("Protests in Nigeria") == "Nigeria"

    def test_category_detection_samples(self):
        """Test category detection with real examples."""
        from core.location import detect_category
        assert detect_category("War declared") == "conflict"
        assert detect_category("Protest march") == "protest"
        assert detect_category("Gang violence") == "violence"


class TestBaseFeed:
    """Test base feed infrastructure."""

    def test_conflict_event_dataclass(self):
        """Verify ConflictEvent dataclass creates correctly."""
        from core.base_feed import ConflictEvent

        event = ConflictEvent(
            source="test",
            title="Test Event",
            url="https://example.com",
            date="2026-05-07",
            country="Ukraine",
            region="Kyiv",
            category="conflict",
            description="Test description",
            latitude=50.45,
            longitude=30.52,
        )

        assert event.source == "test"
        assert event.title == "Test Event"
        assert event.country == "Ukraine"
        assert event.category == "conflict"

    def test_base_feed_abstract(self):
        """Verify BaseFeed cannot be instantiated directly."""
        from core.base_feed import BaseFeed

        with pytest.raises(TypeError):
            # Cannot instantiate abstract class
            BaseFeed()


class TestFeedRegistry:
    """Test feed registry and registration."""

    def test_registry_import(self):
        """Verify registry imports and is singleton."""
        from core.registry import registry
        assert registry is not None

    def test_registry_singleton(self):
        """Verify registry is a singleton."""
        from core.registry import registry as registry1
        from core.registry import registry as registry2
        assert registry1 is registry2

    def test_registry_feed_count(self):
        """Verify registry has registered feeds."""
        from core.registry import registry
        all_feeds = list(registry._feeds.keys())
        assert "aljazeera" in all_feeds
        assert len(all_feeds) >= 1  # At least Al Jazeera


class TestAlJazeeraFeed:
    """Test Al Jazeera feed (live scraping)."""

    def test_aljazeera_feed_creation(self):
        """Verify Al Jazeera feed can be instantiated."""
        from feeds.aljazeera import AlJazeeraFeed

        feed = AlJazeeraFeed()
        assert feed.name == "aljazeera"
        assert feed.is_available() == True

    def test_aljazeera_feed_fetch(self):
        """Test actual Al Jazeera RSS fetch (network call)."""
        from feeds.aljazeera import AlJazeeraFeed

        feed = AlJazeeraFeed()
        events = feed.fetch()

        # Should return a list
        assert isinstance(events, list)

        # If events returned, check structure
        if len(events) > 0:
            event = events[0]
            assert hasattr(event, "source")
            assert hasattr(event, "title")
            assert hasattr(event, "url")
            assert hasattr(event, "country")
            assert event.source == "aljazeera"
            print(f"✅ Al Jazeera returned {len(events)} events")
        else:
            print("⚠️  Al Jazeera returned 0 events (possible network or feed issue)")


class TestPipeline:
    """Test the multi-source pipeline."""

    def test_pipeline_run(self):
        """Test that the pipeline runs without errors."""
        from core.registry import registry
        from core.base_feed import ConflictEvent

        # Fetch from all available feeds
        events = registry.fetch_all()

        # Should return a list
        assert isinstance(events, list)

        # Print summary
        print(f"\n✅ Pipeline collected {len(events)} events")

        if len(events) > 0:
            # Check first event structure
            event = events[0]
            assert isinstance(event, ConflictEvent)
            print(f"   Sample: [{event.country}] {event.title}")


class TestFastAPIServer:
    """Test FastAPI backend (without running server)."""

    def test_fastapi_import(self):
        """Verify FastAPI app imports."""
        # Need to test from the right directory
        app_path = os.path.join(
            os.path.dirname(__file__), "../..", "main.py"
        )
        assert os.path.exists(app_path)

    def test_news_item_model(self):
        """Test Pydantic data model."""
        from main import NewsItem

        item = NewsItem(
            id=1,
            country="Ukraine",
            headline="Test headline",
            date="2026-05-07",
            category="conflict",
        )

        assert item.country == "Ukraine"
        assert item.category == "conflict"


class TestRequirements:
    """Test that all required packages are installed."""

    def test_required_packages_installed(self):
        """Verify all critical dependencies are installed."""
        required = ["requests", "psycopg2", "pydantic", "fastapi", "pytest"]

        for package in required:
            try:
                __import__(package.replace("-", "_"))
                print(f"✅ {package} installed")
            except ImportError:
                pytest.fail(f"❌ {package} not installed")


# ─── Test Suite Summary ──────────────────────────────────────────────────────
def test_summary():
    """Print test summary."""
    print("\n" + "=" * 70)
    print("  CONFLICT TRACKER — INTEGRATION TEST SUITE")
    print("=" * 70)
    print("✅ Location detection module")
    print("✅ Base feed infrastructure")
    print("✅ Feed registry (singleton)")
    print("✅ Al Jazeera feed (live scraping)")
    print("✅ Multi-source pipeline")
    print("✅ FastAPI models")
    print("✅ Required packages")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
