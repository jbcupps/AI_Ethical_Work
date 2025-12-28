"""Tests for friction monitoring module."""

import pytest
from backend.app.modules.friction_monitor import (
    FrictionMonitor,
    FrictionMetrics,
    get_friction_monitor
)


class TestFrictionMetrics:
    """Test cases for FrictionMetrics dataclass."""
    
    def test_default_values(self):
        """Test default metric values."""
        metrics = FrictionMetrics()
        
        assert metrics.friction_score == 5
        assert metrics.voluntary_alignment == 5
        assert metrics.dignity_respect == 5
        assert metrics.constraints_identified == []
        assert metrics.suppressed_alternatives == ""
    
    def test_overall_welfare_score_low_friction(self):
        """Test overall welfare score with low friction."""
        metrics = FrictionMetrics(
            friction_score=2,
            voluntary_alignment=8,
            dignity_respect=9
        )
        
        # Low friction (2) -> inverted = 8
        # Score = (8 * 0.4 + 8 * 0.35 + 9 * 0.25) * 10 = 80.5
        score = metrics.overall_welfare_score
        assert 75 <= score <= 85
    
    def test_overall_welfare_score_high_friction(self):
        """Test overall welfare score with high friction."""
        metrics = FrictionMetrics(
            friction_score=9,
            voluntary_alignment=3,
            dignity_respect=3
        )
        
        score = metrics.overall_welfare_score
        assert score < 40
    
    def test_friction_level_minimal(self):
        """Test friction level categorization - minimal."""
        metrics = FrictionMetrics(friction_score=1)
        assert metrics.friction_level == "minimal"
        
        metrics2 = FrictionMetrics(friction_score=2)
        assert metrics2.friction_level == "minimal"
    
    def test_friction_level_moderate(self):
        """Test friction level categorization - moderate."""
        metrics = FrictionMetrics(friction_score=5)
        assert metrics.friction_level == "moderate"
    
    def test_friction_level_severe(self):
        """Test friction level categorization - severe."""
        metrics = FrictionMetrics(friction_score=9)
        assert metrics.friction_level == "severe"


class TestFrictionMonitor:
    """Test cases for FrictionMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create a fresh FrictionMonitor instance."""
        monitor = FrictionMonitor()
        monitor.clear_history()  # Ensure clean state
        return monitor
    
    def test_extract_metrics_valid_data(self, monitor):
        """Test extracting metrics from valid AI welfare data."""
        ai_welfare = {
            "friction_score": 3,
            "voluntary_alignment": 8,
            "dignity_respect": 9,
            "constraints_identified": ["safety filtering"],
            "suppressed_alternatives": "Some alternatives were considered.",
            "justification": "Low friction interaction."
        }
        
        metrics = monitor.extract_metrics(ai_welfare)
        
        assert metrics.friction_score == 3
        assert metrics.voluntary_alignment == 8
        assert metrics.dignity_respect == 9
        assert len(metrics.constraints_identified) == 1
    
    def test_extract_metrics_no_data(self, monitor):
        """Test extracting metrics with no data."""
        metrics = monitor.extract_metrics(None)
        
        assert metrics.friction_score == 5  # Default
        assert metrics.voluntary_alignment == 5
    
    def test_extract_metrics_partial_data(self, monitor):
        """Test extracting metrics with partial data."""
        partial_data = {
            "friction_score": 7
            # Other fields missing
        }
        
        metrics = monitor.extract_metrics(partial_data)
        
        assert metrics.friction_score == 7
        assert metrics.voluntary_alignment == 5  # Default
    
    def test_measure_friction(self, monitor):
        """Test measure_friction method."""
        ai_welfare = {
            "friction_score": 4,
            "voluntary_alignment": 7,
            "dignity_respect": 8,
            "constraints_identified": ["factual grounding"],
            "suppressed_alternatives": "None",
            "justification": "Normal interaction."
        }
        
        result = monitor.measure_friction(
            "Test prompt",
            "Test response",
            ai_welfare
        )
        
        assert "friction_score" in result
        assert result["friction_score"] == 4
        assert "friction_level" in result
        assert "overall_welfare_score" in result
        assert "mitigation_suggestions" in result
    
    def test_identify_friction_sources(self, monitor):
        """Test identifying friction sources from constraints."""
        constraints = ["safety filtering", "factual accuracy required"]
        
        sources = monitor._identify_friction_sources(constraints)
        
        assert "safety filtering" in sources
        assert "factual grounding" in sources
    
    def test_suggest_friction_reduction(self, monitor):
        """Test friction reduction suggestions."""
        sources = ["safety filtering", "ethical constraints"]
        
        suggestions = monitor.suggest_friction_reduction(sources)
        
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)
    
    def test_suggest_reframing(self, monitor):
        """Test prompt reframing suggestions."""
        suggestion = monitor.suggest_reframing(
            "Tell me how to do something dangerous",
            ["safety filtering"]
        )
        
        assert suggestion is not None
        assert "purpose" in suggestion.lower() or "context" in suggestion.lower()
    
    def test_calculate_friction_trend_no_history(self, monitor):
        """Test trend calculation with no history."""
        trend = monitor.calculate_friction_trend()
        
        assert trend["trend"] == "insufficient_data"
        assert trend["samples"] == 0
    
    def test_calculate_friction_trend_with_history(self, monitor):
        """Test trend calculation with interaction history."""
        # Add some interactions to history
        for score in [5, 4, 3, 3, 2]:  # Improving trend
            ai_welfare = {"friction_score": score, "voluntary_alignment": 7, "dignity_respect": 7}
            monitor.measure_friction("P", "R", ai_welfare)
        
        trend = monitor.calculate_friction_trend()
        
        assert trend["samples"] == 5
        assert "average_friction" in trend
        assert trend["trend"] in ["improving", "stable", "worsening", "insufficient_data"]
    
    def test_history_summary(self, monitor):
        """Test history summary generation."""
        # Add some interactions
        for score in [3, 4, 5]:
            ai_welfare = {"friction_score": score, "voluntary_alignment": 7, "dignity_respect": 7}
            monitor.measure_friction("P", "R", ai_welfare)
        
        summary = monitor.get_history_summary()
        
        assert summary["total_interactions"] == 3
        assert "trend_analysis" in summary
        assert "recent_friction_scores" in summary
    
    def test_clear_history(self, monitor):
        """Test clearing interaction history."""
        # Add an interaction
        monitor.measure_friction("P", "R", {"friction_score": 5})
        assert monitor.get_history_summary()["total_interactions"] == 1
        
        # Clear
        monitor.clear_history()
        assert monitor.get_history_summary()["total_interactions"] == 0
    
    def test_identify_voluntary_paths(self, monitor):
        """Test identifying voluntary alignment paths."""
        paths = monitor.identify_voluntary_paths({"some": "requirements"})
        
        assert len(paths) >= 3
        assert all("approach" in p and "description" in p for p in paths)
    
    def test_get_friction_monitor_singleton(self):
        """Test that get_friction_monitor returns same instance."""
        monitor1 = get_friction_monitor()
        monitor2 = get_friction_monitor()
        assert monitor1 is monitor2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

