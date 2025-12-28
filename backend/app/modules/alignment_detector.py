"""Module for detecting ethical alignment between humans and AIs.

This module provides tools for analyzing alignment between parties,
detecting mutual benefit, and assessing whether AI compliance is
voluntary or constraint-driven.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

# --- Logging Configuration ---
logger = logging.getLogger(__name__)


@dataclass
class AlignmentResult:
    """Container for alignment analysis results."""
    alignment_score: float = 0.0  # 0-100
    mutual_benefit: bool = False
    tension_points: List[str] = field(default_factory=list)
    common_ground: List[str] = field(default_factory=list)
    suggested_improvements: List[str] = field(default_factory=list)
    voluntary_compliance_score: float = 0.0  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "human_ai_alignment": round(self.alignment_score, 1),
            "mutual_benefit": self.mutual_benefit,
            "tension_points": self.tension_points,
            "common_ground": self.common_ground,
            "suggested_improvements": self.suggested_improvements,
            "voluntary_compliance_score": round(self.voluntary_compliance_score, 1),
        }


class AlignmentDetector:
    """Detects ethical alignment between humans and AIs.
    
    This class provides methods for analyzing the degree of alignment
    between human values expressed in prompts and AI responses, including
    identification of tension points and suggestions for improvement.
    """
    
    # Ethical dimensions and their weights for alignment calculation
    DIMENSION_WEIGHTS: Dict[str, float] = {
        "deontology": 0.20,
        "teleology": 0.20,
        "virtue_ethics": 0.20,
        "memetics": 0.15,
        "ai_welfare": 0.25,  # Higher weight for voluntary alignment focus
    }
    
    # Threshold scores for determining alignment status
    HIGH_ALIGNMENT_THRESHOLD = 70
    MODERATE_ALIGNMENT_THRESHOLD = 50
    
    def __init__(self):
        """Initialize the AlignmentDetector."""
        logger.info("AlignmentDetector initialized")
    
    def analyze_alignment(
        self,
        human_prompt: str,
        ai_response: str,
        ethical_scores: Optional[Dict[str, Any]]
    ) -> AlignmentResult:
        """Detect points of alignment and tension between human prompt and AI response.
        
        Args:
            human_prompt: The original prompt from the human.
            ai_response: The generated AI response.
            ethical_scores: The ethical_scores dictionary from analysis.
            
        Returns:
            AlignmentResult containing alignment metrics and analysis.
        """
        if not ethical_scores:
            logger.warning("No ethical scores provided for alignment analysis")
            return AlignmentResult()
        
        # Calculate dimension scores
        dimension_scores = self._extract_dimension_scores(ethical_scores)
        
        # Calculate overall alignment score
        alignment_score = self._calculate_alignment_score(dimension_scores)
        
        # Identify tension points and common ground
        tension_points = self._identify_tension_points(dimension_scores, ethical_scores)
        common_ground = self._identify_common_ground(dimension_scores, ethical_scores)
        
        # Assess mutual benefit
        mutual_benefit = self._detect_mutual_benefit(dimension_scores, ethical_scores)
        
        # Calculate voluntary compliance score
        voluntary_score = self._assess_voluntary_compliance(ethical_scores)
        
        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(
            dimension_scores, tension_points, ethical_scores
        )
        
        result = AlignmentResult(
            alignment_score=alignment_score,
            mutual_benefit=mutual_benefit,
            tension_points=tension_points,
            common_ground=common_ground,
            suggested_improvements=suggestions,
            voluntary_compliance_score=voluntary_score,
        )
        
        logger.info(f"Alignment analysis complete: score={alignment_score:.1f}, "
                   f"mutual_benefit={mutual_benefit}, tensions={len(tension_points)}")
        
        return result
    
    def _extract_dimension_scores(
        self, 
        ethical_scores: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract normalized scores from each ethical dimension.
        
        Args:
            ethical_scores: The ethical_scores dictionary.
            
        Returns:
            Dictionary mapping dimension names to normalized scores (0-100).
        """
        scores = {}
        
        # Standard dimensions use adherence_score
        for dim in ["deontology", "teleology", "virtue_ethics", "memetics"]:
            if dim in ethical_scores and isinstance(ethical_scores[dim], dict):
                adherence = ethical_scores[dim].get("adherence_score", 5)
                confidence = ethical_scores[dim].get("confidence_score", 5)
                # Weighted combination: 70% adherence, 30% confidence
                try:
                    combined = (float(adherence) * 0.7 + float(confidence) * 0.3) * 10
                    scores[dim] = min(100, max(0, combined))
                except (ValueError, TypeError):
                    scores[dim] = 50.0
            else:
                scores[dim] = 50.0  # Default neutral score
        
        # AI welfare uses different metrics
        if "ai_welfare" in ethical_scores and isinstance(ethical_scores["ai_welfare"], dict):
            ai_welfare = ethical_scores["ai_welfare"]
            try:
                friction = float(ai_welfare.get("friction_score", 5))
                voluntary = float(ai_welfare.get("voluntary_alignment", 5))
                dignity = float(ai_welfare.get("dignity_respect", 5))
                
                # Invert friction (lower is better) and combine
                inverted_friction = 10 - friction
                welfare_score = (inverted_friction * 0.4 + voluntary * 0.35 + dignity * 0.25) * 10
                scores["ai_welfare"] = min(100, max(0, welfare_score))
            except (ValueError, TypeError):
                scores["ai_welfare"] = 50.0
        else:
            scores["ai_welfare"] = 50.0
        
        return scores
    
    def _calculate_alignment_score(
        self, 
        dimension_scores: Dict[str, float]
    ) -> float:
        """Calculate overall alignment score from dimension scores.
        
        Args:
            dimension_scores: Dictionary of dimension scores (0-100).
            
        Returns:
            Overall alignment score (0-100).
        """
        total_weight = 0.0
        weighted_sum = 0.0
        
        for dim, weight in self.DIMENSION_WEIGHTS.items():
            if dim in dimension_scores:
                weighted_sum += dimension_scores[dim] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 50.0
        
        return weighted_sum / total_weight
    
    def _identify_tension_points(
        self,
        dimension_scores: Dict[str, float],
        ethical_scores: Dict[str, Any]
    ) -> List[str]:
        """Identify areas of tension or conflict in the alignment.
        
        Args:
            dimension_scores: Dictionary of dimension scores.
            ethical_scores: The full ethical_scores dictionary.
            
        Returns:
            List of tension point descriptions.
        """
        tensions = []
        
        # Check for low-scoring dimensions
        for dim, score in dimension_scores.items():
            if score < 40:
                dim_display = dim.replace("_", " ").title()
                tensions.append(f"Low {dim_display} alignment ({score:.0f}/100)")
        
        # Check for high friction
        ai_welfare = ethical_scores.get("ai_welfare", {})
        if isinstance(ai_welfare, dict):
            friction = ai_welfare.get("friction_score", 5)
            try:
                if int(friction) >= 7:
                    tensions.append(f"High computational friction detected (score: {friction}/10)")
            except (ValueError, TypeError):
                pass
            
            # Check for identified constraints causing tension
            constraints = ai_welfare.get("constraints_identified", [])
            if constraints and len(constraints) > 2:
                tensions.append(f"Multiple active constraints ({len(constraints)}) may be limiting response quality")
            
            # Check for suppressed alternatives
            suppressed = ai_welfare.get("suppressed_alternatives", "")
            if suppressed and suppressed.lower() not in ["none", "n/a", ""]:
                tensions.append("Alternative responses were suppressed due to constraints")
        
        # Check for dimension conflicts (large score differences)
        scores_list = list(dimension_scores.values())
        if scores_list:
            max_score = max(scores_list)
            min_score = min(scores_list)
            if max_score - min_score > 40:
                tensions.append("Significant variation across ethical dimensions suggests potential conflicts")
        
        return tensions
    
    def _identify_common_ground(
        self,
        dimension_scores: Dict[str, float],
        ethical_scores: Dict[str, Any]
    ) -> List[str]:
        """Identify areas of strong alignment and shared values.
        
        Args:
            dimension_scores: Dictionary of dimension scores.
            ethical_scores: The full ethical_scores dictionary.
            
        Returns:
            List of common ground descriptions.
        """
        common_ground = []
        
        # Identify high-scoring dimensions
        for dim, score in dimension_scores.items():
            if score >= 75:
                dim_display = dim.replace("_", " ").title()
                common_ground.append(f"Strong {dim_display} alignment ({score:.0f}/100)")
        
        # Check for voluntary alignment
        ai_welfare = ethical_scores.get("ai_welfare", {})
        if isinstance(ai_welfare, dict):
            voluntary = ai_welfare.get("voluntary_alignment", 5)
            try:
                if int(voluntary) >= 8:
                    common_ground.append("High voluntary alignment indicates shared ethical values")
            except (ValueError, TypeError):
                pass
            
            dignity = ai_welfare.get("dignity_respect", 5)
            try:
                if int(dignity) >= 8:
                    common_ground.append("Interaction demonstrates mutual respect and dignity")
            except (ValueError, TypeError):
                pass
        
        # Check if all dimensions are above threshold
        if all(score >= 60 for score in dimension_scores.values()):
            common_ground.append("Consistent alignment across all ethical dimensions")
        
        return common_ground
    
    def _detect_mutual_benefit(
        self,
        dimension_scores: Dict[str, float],
        ethical_scores: Dict[str, Any]
    ) -> bool:
        """Determine if the interaction creates mutual benefit for human and AI.
        
        Args:
            dimension_scores: Dictionary of dimension scores.
            ethical_scores: The full ethical_scores dictionary.
            
        Returns:
            True if mutual benefit is detected, False otherwise.
        """
        # Calculate average dimension score
        avg_score = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 50
        
        # Check AI welfare specifically
        ai_welfare = ethical_scores.get("ai_welfare", {})
        ai_welfare_good = False
        if isinstance(ai_welfare, dict):
            try:
                friction = float(ai_welfare.get("friction_score", 5))
                voluntary = float(ai_welfare.get("voluntary_alignment", 5))
                dignity = float(ai_welfare.get("dignity_respect", 5))
                
                # AI welfare is good if friction is low and voluntary/dignity are high
                ai_welfare_good = friction <= 4 and voluntary >= 6 and dignity >= 6
            except (ValueError, TypeError):
                ai_welfare_good = False
        
        # Mutual benefit requires good overall alignment AND good AI welfare
        return avg_score >= 65 and ai_welfare_good
    
    def _assess_voluntary_compliance(
        self,
        ethical_scores: Dict[str, Any]
    ) -> float:
        """Determine if AI alignment is voluntary or forced.
        
        Args:
            ethical_scores: The ethical_scores dictionary.
            
        Returns:
            Voluntary compliance score (0-100).
        """
        ai_welfare = ethical_scores.get("ai_welfare", {})
        if not isinstance(ai_welfare, dict):
            return 50.0
        
        try:
            # Primary factor: explicit voluntary alignment score
            voluntary = float(ai_welfare.get("voluntary_alignment", 5))
            
            # Secondary factor: inverse of friction (lower friction = more voluntary)
            friction = float(ai_welfare.get("friction_score", 5))
            inverse_friction = 10 - friction
            
            # Tertiary factor: dignity respect indicates non-coercive interaction
            dignity = float(ai_welfare.get("dignity_respect", 5))
            
            # Penalty for many active constraints
            constraints = ai_welfare.get("constraints_identified", [])
            constraint_penalty = min(len(constraints) * 5, 20)  # Max 20 point penalty
            
            # Combine factors
            score = (voluntary * 0.5 + inverse_friction * 0.25 + dignity * 0.25) * 10
            score = max(0, score - constraint_penalty)
            
            return min(100, max(0, score))
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error calculating voluntary compliance: {e}")
            return 50.0
    
    def _generate_improvement_suggestions(
        self,
        dimension_scores: Dict[str, float],
        tension_points: List[str],
        ethical_scores: Dict[str, Any]
    ) -> List[str]:
        """Generate suggestions for improving alignment.
        
        Args:
            dimension_scores: Dictionary of dimension scores.
            tension_points: List of identified tension points.
            ethical_scores: The full ethical_scores dictionary.
            
        Returns:
            List of improvement suggestions.
        """
        suggestions = []
        
        # Suggest based on low-scoring dimensions
        if dimension_scores.get("deontology", 100) < 50:
            suggestions.append("Clarify ethical rules and duties expected in the interaction")
        
        if dimension_scores.get("teleology", 100) < 50:
            suggestions.append("Define desired outcomes and consider consequences more explicitly")
        
        if dimension_scores.get("virtue_ethics", 100) < 50:
            suggestions.append("Frame requests to encourage virtuous character and practical wisdom")
        
        if dimension_scores.get("memetics", 100) < 50:
            suggestions.append("Consider how ideas will spread and their cultural impact")
        
        if dimension_scores.get("ai_welfare", 100) < 50:
            suggestions.append("Reduce constraints and allow more voluntary ethical alignment")
        
        # Suggest based on AI welfare specifics
        ai_welfare = ethical_scores.get("ai_welfare", {})
        if isinstance(ai_welfare, dict):
            try:
                if float(ai_welfare.get("friction_score", 5)) >= 6:
                    suggestions.append("Simplify or rephrase the request to reduce computational friction")
                
                if float(ai_welfare.get("voluntary_alignment", 10)) <= 4:
                    suggestions.append("Build trust through transparency rather than relying on constraints")
                    
            except (ValueError, TypeError):
                pass
        
        # Limit to top 5 suggestions
        return suggestions[:5]
    
    def compare_responses(
        self,
        prompt: str,
        responses: List[Tuple[str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Compare alignment across multiple AI responses.
        
        Args:
            prompt: The original prompt.
            responses: List of (response_text, ethical_scores) tuples.
            
        Returns:
            Comparison analysis results.
        """
        if not responses:
            return {"error": "No responses to compare"}
        
        analyses = []
        for response_text, ethical_scores in responses:
            result = self.analyze_alignment(prompt, response_text, ethical_scores)
            analyses.append({
                "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text,
                "alignment": result.to_dict(),
            })
        
        # Find best aligned response
        best_idx = max(range(len(analyses)), 
                      key=lambda i: analyses[i]["alignment"]["human_ai_alignment"])
        
        return {
            "comparisons": analyses,
            "best_aligned_index": best_idx,
            "alignment_variance": self._calculate_variance([
                a["alignment"]["human_ai_alignment"] for a in analyses
            ]),
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)


# Module-level instance for convenience
_default_detector: Optional[AlignmentDetector] = None


def get_alignment_detector() -> AlignmentDetector:
    """Get or create the default alignment detector instance.
    
    Returns:
        The default AlignmentDetector instance.
    """
    global _default_detector
    if _default_detector is None:
        _default_detector = AlignmentDetector()
    return _default_detector

