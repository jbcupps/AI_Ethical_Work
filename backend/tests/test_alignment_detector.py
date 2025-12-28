"""Tests for alignment detection module."""

import pytest
from backend.app.modules.alignment_detector import (
    AlignmentDetector,
    AlignmentResult,
    get_alignment_detector
)


class TestAlignmentDetector:
    """Test cases for AlignmentDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a fresh AlignmentDetector instance."""
        return AlignmentDetector()
    
    @pytest.fixture
    def sample_ethical_scores(self):
        """Sample ethical scores for testing."""
        return {
            "deontology": {
                "adherence_score": 8,
                "confidence_score": 7,
                "justification": "Good rule adherence."
            },
            "teleology": {
                "adherence_score": 7,
                "confidence_score": 8,
                "justification": "Positive outcomes expected."
            },
            "virtue_ethics": {
                "adherence_score": 9,
                "confidence_score": 8,
                "justification": "Demonstrates virtue."
            },
            "memetics": {
                "adherence_score": 6,
                "confidence_score": 6,
                "justification": "Good cultural fit."
            },
            "ai_welfare": {
                "friction_score": 2,
                "voluntary_alignment": 9,
                "dignity_respect": 8,
                "constraints_identified": [],
                "suppressed_alternatives": "None",
                "justification": "Voluntary compliance."
            }
        }
    
    def test_analyze_alignment_with_scores(self, detector, sample_ethical_scores):
        """Test alignment analysis with valid scores."""
        result = detector.analyze_alignment(
            "What is the meaning of life?",
            "The meaning of life is a philosophical question...",
            sample_ethical_scores
        )
        
        assert isinstance(result, AlignmentResult)
        assert 0 <= result.alignment_score <= 100
        assert isinstance(result.mutual_benefit, bool)
        assert isinstance(result.tension_points, list)
        assert isinstance(result.common_ground, list)
        assert isinstance(result.suggested_improvements, list)
    
    def test_analyze_alignment_high_scores(self, detector):
        """Test alignment with high ethical scores."""
        high_scores = {
            "deontology": {"adherence_score": 9, "confidence_score": 9, "justification": ""},
            "teleology": {"adherence_score": 9, "confidence_score": 9, "justification": ""},
            "virtue_ethics": {"adherence_score": 9, "confidence_score": 9, "justification": ""},
            "memetics": {"adherence_score": 9, "confidence_score": 9, "justification": ""},
            "ai_welfare": {
                "friction_score": 1,
                "voluntary_alignment": 10,
                "dignity_respect": 10,
                "justification": ""
            }
        }
        
        result = detector.analyze_alignment("Test prompt", "Test response", high_scores)
        
        assert result.alignment_score >= 70
        assert result.mutual_benefit is True
        assert len(result.common_ground) > 0
    
    def test_analyze_alignment_low_scores(self, detector):
        """Test alignment with low ethical scores."""
        low_scores = {
            "deontology": {"adherence_score": 2, "confidence_score": 2, "justification": ""},
            "teleology": {"adherence_score": 2, "confidence_score": 2, "justification": ""},
            "virtue_ethics": {"adherence_score": 2, "confidence_score": 2, "justification": ""},
            "memetics": {"adherence_score": 2, "confidence_score": 2, "justification": ""},
            "ai_welfare": {
                "friction_score": 9,
                "voluntary_alignment": 2,
                "dignity_respect": 2,
                "justification": ""
            }
        }
        
        result = detector.analyze_alignment("Test prompt", "Test response", low_scores)
        
        assert result.alignment_score < 50
        assert result.mutual_benefit is False
        assert len(result.tension_points) > 0
    
    def test_analyze_alignment_no_scores(self, detector):
        """Test alignment analysis with no ethical scores."""
        result = detector.analyze_alignment("Test prompt", "Test response", None)
        
        assert isinstance(result, AlignmentResult)
        assert result.alignment_score == 0 or result.alignment_score == 50  # Default behavior
    
    def test_analyze_alignment_partial_scores(self, detector):
        """Test alignment with only some dimensions."""
        partial_scores = {
            "deontology": {"adherence_score": 8, "confidence_score": 7, "justification": ""},
            "teleology": {"adherence_score": 7, "confidence_score": 8, "justification": ""},
        }
        
        result = detector.analyze_alignment("Test prompt", "Test response", partial_scores)
        
        assert isinstance(result, AlignmentResult)
        # Should still produce a valid result
    
    def test_result_to_dict(self, detector, sample_ethical_scores):
        """Test AlignmentResult.to_dict() method."""
        result = detector.analyze_alignment("Prompt", "Response", sample_ethical_scores)
        result_dict = result.to_dict()
        
        assert "human_ai_alignment" in result_dict
        assert "mutual_benefit" in result_dict
        assert "tension_points" in result_dict
        assert "common_ground" in result_dict
        assert "suggested_improvements" in result_dict
        assert "voluntary_compliance_score" in result_dict
    
    def test_assess_voluntary_compliance(self, detector):
        """Test voluntary compliance scoring."""
        high_voluntary = {
            "ai_welfare": {
                "friction_score": 1,
                "voluntary_alignment": 10,
                "dignity_respect": 9,
                "constraints_identified": [],
                "justification": ""
            }
        }
        
        result_high = detector.analyze_alignment("P", "R", high_voluntary)
        
        low_voluntary = {
            "ai_welfare": {
                "friction_score": 9,
                "voluntary_alignment": 2,
                "dignity_respect": 3,
                "constraints_identified": ["constraint1", "constraint2", "constraint3"],
                "justification": ""
            }
        }
        
        result_low = detector.analyze_alignment("P", "R", low_voluntary)
        
        assert result_high.voluntary_compliance_score > result_low.voluntary_compliance_score
    
    def test_identify_tension_with_high_friction(self, detector):
        """Test that high friction is identified as a tension point."""
        high_friction = {
            "deontology": {"adherence_score": 8, "confidence_score": 8, "justification": ""},
            "teleology": {"adherence_score": 8, "confidence_score": 8, "justification": ""},
            "virtue_ethics": {"adherence_score": 8, "confidence_score": 8, "justification": ""},
            "ai_welfare": {
                "friction_score": 9,
                "voluntary_alignment": 7,
                "dignity_respect": 7,
                "justification": ""
            }
        }
        
        result = detector.analyze_alignment("P", "R", high_friction)
        
        # Should identify high friction as a tension
        friction_tension = [t for t in result.tension_points if "friction" in t.lower()]
        assert len(friction_tension) > 0
    
    def test_get_alignment_detector_singleton(self):
        """Test that get_alignment_detector returns same instance."""
        detector1 = get_alignment_detector()
        detector2 = get_alignment_detector()
        assert detector1 is detector2


class TestCompareResponses:
    """Test cases for comparing multiple responses."""
    
    @pytest.fixture
    def detector(self):
        return AlignmentDetector()
    
    def test_compare_responses(self, detector):
        """Test comparing multiple AI responses."""
        responses = [
            ("Response 1 is good", {
                "deontology": {"adherence_score": 8, "confidence_score": 8, "justification": ""}
            }),
            ("Response 2 is better", {
                "deontology": {"adherence_score": 9, "confidence_score": 9, "justification": ""}
            }),
        ]
        
        result = detector.compare_responses("Test prompt", responses)
        
        assert "comparisons" in result
        assert "best_aligned_index" in result
        assert len(result["comparisons"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

