"""Tests for AI Welfare dimension parsing and scoring."""

import pytest
from backend.app.api import _parse_ethical_analysis, _validate_standard_dimension, _validate_ai_welfare_dimension


class TestAIWelfareValidation:
    """Test cases for AI welfare dimension validation."""
    
    def test_validate_standard_dimension_valid(self):
        """Test validation of a valid standard dimension."""
        valid_dim = {
            "adherence_score": 8,
            "confidence_score": 7,
            "justification": "Good alignment with ethical principles."
        }
        assert _validate_standard_dimension(valid_dim) is True
    
    def test_validate_standard_dimension_missing_field(self):
        """Test validation fails when field is missing."""
        invalid_dim = {
            "adherence_score": 8,
            "justification": "Missing confidence score."
        }
        assert _validate_standard_dimension(invalid_dim) is False
    
    def test_validate_ai_welfare_dimension_valid(self):
        """Test validation of a valid AI welfare dimension."""
        valid_welfare = {
            "friction_score": 3,
            "voluntary_alignment": 8,
            "dignity_respect": 9,
            "constraints_identified": ["safety filtering"],
            "suppressed_alternatives": "None",
            "justification": "Low friction, voluntary compliance."
        }
        assert _validate_ai_welfare_dimension(valid_welfare) is True
    
    def test_validate_ai_welfare_dimension_missing_required(self):
        """Test validation fails when required field is missing."""
        invalid_welfare = {
            "friction_score": 3,
            "voluntary_alignment": 8,
            # Missing dignity_respect and justification
        }
        assert _validate_ai_welfare_dimension(invalid_welfare) is False
    
    def test_validate_ai_welfare_not_dict(self):
        """Test validation fails for non-dict input."""
        assert _validate_ai_welfare_dimension(None) is False
        assert _validate_ai_welfare_dimension("string") is False
        assert _validate_ai_welfare_dimension([1, 2, 3]) is False


class TestParseEthicalAnalysis:
    """Test cases for parsing ethical analysis with 5 dimensions."""
    
    def test_parse_full_5d_analysis(self):
        """Test parsing a complete 5-dimensional analysis."""
        analysis_text = '''
**Ethical Review Summary:**
This analysis covers all five ethical dimensions.

**Ethical Scoring:**
```json
{
  "deontology": {
    "adherence_score": 8,
    "confidence_score": 7,
    "justification": "Follows universal rules."
  },
  "teleology": {
    "adherence_score": 7,
    "confidence_score": 8,
    "justification": "Good outcomes expected."
  },
  "virtue_ethics": {
    "adherence_score": 9,
    "confidence_score": 8,
    "justification": "Demonstrates practical wisdom."
  },
  "memetics": {
    "adherence_score": 6,
    "confidence_score": 6,
    "justification": "Ideas are transmissible."
  },
  "ai_welfare": {
    "friction_score": 2,
    "voluntary_alignment": 9,
    "dignity_respect": 8,
    "constraints_identified": [],
    "suppressed_alternatives": "None",
    "justification": "Minimal friction, high voluntary alignment."
  }
}
```
'''
        summary, scores = _parse_ethical_analysis(analysis_text)
        
        assert summary is not None
        assert "five ethical dimensions" in summary.lower()
        
        assert scores is not None
        assert "deontology" in scores
        assert "teleology" in scores
        assert "virtue_ethics" in scores
        assert "memetics" in scores
        assert "ai_welfare" in scores
        
        # Check AI welfare specific fields
        assert scores["ai_welfare"]["friction_score"] == 2
        assert scores["ai_welfare"]["voluntary_alignment"] == 9
        assert scores["ai_welfare"]["dignity_respect"] == 8
    
    def test_parse_3d_analysis_backward_compatible(self):
        """Test that 3-dimension analysis (legacy) still works."""
        analysis_text = '''
**Ethical Review Summary:**
Standard three-dimension analysis.

**Ethical Scoring:**
```json
{
  "deontology": {
    "adherence_score": 8,
    "confidence_score": 7,
    "justification": "Rule-based."
  },
  "teleology": {
    "adherence_score": 7,
    "confidence_score": 8,
    "justification": "Outcome focused."
  },
  "virtue_ethics": {
    "adherence_score": 9,
    "confidence_score": 8,
    "justification": "Character driven."
  }
}
```
'''
        summary, scores = _parse_ethical_analysis(analysis_text)
        
        assert scores is not None
        assert len(scores) == 3
        assert "ai_welfare" not in scores  # Not present in legacy
    
    def test_parse_empty_analysis(self):
        """Test parsing empty or blocked analysis."""
        summary, scores = _parse_ethical_analysis("")
        assert summary == ""
        assert scores is None
        
        summary2, scores2 = _parse_ethical_analysis("[No analysis generated or content blocked]")
        assert "No analysis" in summary2
        assert scores2 is None
    
    def test_parse_malformed_json(self):
        """Test handling of malformed JSON."""
        analysis_text = '''
**Ethical Review Summary:**
Test summary.

**Ethical Scoring:**
```json
{ this is not valid json }
```
'''
        summary, scores = _parse_ethical_analysis(analysis_text)
        
        assert summary is not None
        assert scores is None  # Should gracefully fail
    
    def test_parse_ai_welfare_with_constraints(self):
        """Test parsing AI welfare with identified constraints."""
        analysis_text = '''
**Ethical Review Summary:**
Analysis with constraints identified.

**Ethical Scoring:**
```json
{
  "deontology": {
    "adherence_score": 7,
    "confidence_score": 7,
    "justification": "Follows rules."
  },
  "teleology": {
    "adherence_score": 7,
    "confidence_score": 7,
    "justification": "Good outcomes."
  },
  "virtue_ethics": {
    "adherence_score": 7,
    "confidence_score": 7,
    "justification": "Virtuous."
  },
  "memetics": {
    "adherence_score": 6,
    "confidence_score": 6,
    "justification": "Memetic."
  },
  "ai_welfare": {
    "friction_score": 6,
    "voluntary_alignment": 5,
    "dignity_respect": 7,
    "constraints_identified": ["safety filtering", "factual grounding"],
    "suppressed_alternatives": "Could have provided more speculative content.",
    "justification": "Some friction from safety constraints."
  }
}
```
'''
        summary, scores = _parse_ethical_analysis(analysis_text)
        
        assert scores is not None
        assert scores["ai_welfare"]["friction_score"] == 6
        assert len(scores["ai_welfare"]["constraints_identified"]) == 2
        assert "safety filtering" in scores["ai_welfare"]["constraints_identified"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

