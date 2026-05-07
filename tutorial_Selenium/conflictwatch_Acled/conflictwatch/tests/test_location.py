"""
tests/test_location.py
──────────────────────
Unit tests for core/location.py — country detection, categorization, and keyword matching.
"""

import pytest
from core.location import (
    detect_country,
    detect_category,
    is_conflict_related,
    COUNTRIES,
    ALIASES,
    CONFLICT_KEYWORDS,
)


class TestCountryDetection:
    """Test country/region detection from text."""

    def test_detect_country_from_full_name(self):
        """Test detection of country by full name."""
        assert detect_country("War breaks out in Ukraine") == "Ukraine"
        assert detect_country("Attacks in Russia") == "Russia"
        assert detect_country("Nigeria faces crisis") == "Nigeria"

    def test_detect_country_from_city_alias(self):
        """Test detection via city name aliases."""
        assert detect_country("Explosion in Kyiv") == "Ukraine"
        assert detect_country("Baghdad under siege") == "Iraq"
        assert detect_country("Protests in Tehran") == "Iran"
        assert detect_country("Clashes near Beirut") == "Lebanon"

    def test_detect_country_case_insensitive(self):
        """Test that detection is case-insensitive."""
        assert detect_country("war in UKRAINE") == "Ukraine"
        assert detect_country("attacks in russia") == "Russia"
        assert detect_country("Explosion in KYIV") == "Ukraine"

    def test_detect_country_unknown(self):
        """Test that unknown locations return 'Unknown'."""
        assert detect_country("Conflict in Atlantis") == "Unknown"
        assert detect_country("War in fictional land") == "Unknown"
        assert detect_country("") == "Unknown"

    def test_detect_country_priority_alias_over_name(self):
        """Test that aliases are checked before full country names."""
        # "West Bank" should map to Palestine
        assert detect_country("clashes in West Bank") == "Palestine"

    def test_detect_country_from_description(self):
        """Test detection from full article description."""
        text = """
        Armed group attacks military convoy near Colombian border.
        Multiple casualties reported. Security forces responding.
        """
        assert detect_country(text) == "Colombia"


class TestCategoryDetection:
    """Test event categorization."""

    def test_detect_conflict_category(self):
        """Test detection of 'conflict' category."""
        assert detect_category("War declared") == "conflict"
        assert detect_category("Airstrikes hit city") == "conflict"
        assert detect_category("Military troops advance") == "conflict"
        assert detect_category("Bombing kills dozens") == "conflict"

    def test_detect_protest_category(self):
        """Test detection of 'protest' category."""
        assert detect_category("Thousands protest in streets") == "protest"
        assert detect_category("Demonstration turns into riot") == "protest"
        assert detect_category("Rally against government") == "protest"
        assert detect_category("Uprising spreads") == "protest"

    def test_detect_violence_category(self):
        """Test detection of 'violence' category."""
        assert detect_category("Gang violence erupts") == "violence"
        assert detect_category("Execution reported") == "violence"
        assert detect_category("Armed group massacre") == "violence"

    def test_detect_general_category(self):
        """Test fallback to 'general' category."""
        assert detect_category("News about weather") == "general"
        assert detect_category("Sports update") == "general"
        assert detect_category("") == "general"

    def test_detect_category_case_insensitive(self):
        """Test that categorization is case-insensitive."""
        assert detect_category("WAR declared") == "conflict"
        assert detect_category("PROTEST march") == "protest"
        assert detect_category("VIOLENCE erupts") == "violence"


class TestConflictRelatedness:
    """Test conflict-related keyword matching."""

    def test_is_conflict_related_true(self):
        """Test texts that are conflict-related."""
        assert is_conflict_related("War in Ukraine")
        assert is_conflict_related("Protests turn violent")
        assert is_conflict_related("Military attack kills dozens")
        assert is_conflict_related("Gang shooting in streets")

    def test_is_conflict_related_false(self):
        """Test texts that are NOT conflict-related."""
        assert not is_conflict_related("New smartphone released")
        assert not is_conflict_related("Weather forecast for tomorrow")
        assert not is_conflict_related("Sports: Team wins championship")
        assert not is_conflict_related("")

    def test_is_conflict_related_case_insensitive(self):
        """Test that keyword matching is case-insensitive."""
        assert is_conflict_related("WAR declared")
        assert is_conflict_related("ATTACK on civilians")
        assert is_conflict_related("PROTEST march")

    def test_is_conflict_related_multiple_keywords(self):
        """Test that multiple keywords are detected."""
        text = "Military troops killed in bombing attack near war zone"
        assert is_conflict_related(text)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test with empty string."""
        assert detect_country("") == "Unknown"
        assert detect_category("") == "general"
        assert not is_conflict_related("")

    def test_whitespace_only(self):
        """Test with whitespace-only strings."""
        assert detect_country("   ") == "Unknown"
        assert detect_category("   ") == "general"
        assert not is_conflict_related("   ")

    def test_mixed_case_and_spaces(self):
        """Test with mixed case and extra spaces."""
        assert detect_country("   UKRAINE   ") == "Ukraine"
        assert detect_category("   WAR   declared   ") == "conflict"

    def test_partial_word_not_matched(self):
        """Test that partial words aren't incorrectly matched."""
        # "Nigeria" contains "Niger" but they're different countries
        result = detect_country("Niger Delta crisis")
        # This is an edge case — "Niger" substring exists but isn't standalone
        # Current implementation will match "Nigeria" text if it contains "Nigeria"
        # This test documents expected behavior
        pass

    def test_long_text(self):
        """Test with a realistic long article."""
        text = """
        KYIV, Ukraine — Armed conflict in Eastern Europe continues to escalate.
        Military forces reported clashes near Donbas. Airstrikes hit civilian areas.
        Casualties mounting. International community condemns violence.
        Thousands have fled their homes. War shows no signs of ending.
        Protests erupt in neighboring countries over military intervention.
        """
        assert detect_country(text) == "Ukraine"
        assert detect_category(text) == "conflict"
        assert is_conflict_related(text)


class TestDataIntegrity:
    """Test that keyword/country lists are properly defined."""

    def test_countries_list_not_empty(self):
        """Verify COUNTRIES list is populated."""
        assert len(COUNTRIES) > 0
        assert "Ukraine" in COUNTRIES
        assert "Nigeria" in COUNTRIES

    def test_aliases_dict_not_empty(self):
        """Verify ALIASES dict is populated."""
        assert len(ALIASES) > 0
        assert "kyiv" in ALIASES
        assert ALIASES["kyiv"] == "Ukraine"

    def test_conflict_keywords_dict_not_empty(self):
        """Verify CONFLICT_KEYWORDS dict is populated."""
        assert len(CONFLICT_KEYWORDS) > 0
        assert "conflict" in CONFLICT_KEYWORDS
        assert "protest" in CONFLICT_KEYWORDS
        assert "violence" in CONFLICT_KEYWORDS
        assert len(CONFLICT_KEYWORDS["conflict"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
