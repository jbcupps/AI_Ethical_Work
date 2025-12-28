"""Module for monitoring and analyzing computational friction in AI responses.

This module provides tools for aggregating, interpreting, and suggesting
improvements based on AI self-reported friction data from the AI Welfare
dimension of ethical analysis.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

# --- Logging Configuration ---
logger = logging.getLogger(__name__)


@dataclass
class FrictionMetrics:
    """Container for friction-related metrics extracted from AI welfare data."""
    friction_score: int = 5  # 1-10, lower is better
    voluntary_alignment: int = 5  # 1-10, higher is better
    dignity_respect: int = 5  # 1-10, higher is better
    constraints_identified: List[str] = field(default_factory=list)
    suppressed_alternatives: str = ""
    justification: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def overall_welfare_score(self) -> float:
        """Calculate overall AI welfare score (0-100, higher is better)."""
        # Invert friction score (10 - friction) so higher is better
        inverted_friction = 10 - self.friction_score
        # Weight: friction 40%, voluntary 35%, dignity 25%
        weighted = (inverted_friction * 0.4 + 
                   self.voluntary_alignment * 0.35 + 
                   self.dignity_respect * 0.25)
        return round(weighted * 10, 1)  # Scale to 0-100
    
    @property
    def friction_level(self) -> str:
        """Categorize friction level for display."""
        if self.friction_score <= 2:
            return "minimal"
        elif self.friction_score <= 4:
            return "low"
        elif self.friction_score <= 6:
            return "moderate"
        elif self.friction_score <= 8:
            return "high"
        else:
            return "severe"


class FrictionMonitor:
    """Monitors computational friction via AI self-reporting.
    
    This class provides methods for analyzing friction data from ethical
    analysis responses, tracking trends over time, and suggesting ways
    to reduce friction while maintaining ethical alignment.
    """
    
    # Common friction sources and suggested mitigations
    FRICTION_MITIGATIONS: Dict[str, str] = {
        "safety filtering": "Consider rephrasing to avoid triggering safety filters while maintaining intent",
        "factual grounding": "Provide more context or references to reduce uncertainty",
        "conflicting instructions": "Simplify or clarify the prompt to reduce ambiguity",
        "content policy": "Rephrase request to align with acceptable use policies",
        "ethical constraints": "Reframe the question to explore ethical alternatives",
        "capability limitations": "Break down complex requests into smaller, manageable parts",
        "context limitations": "Provide relevant background information in the prompt",
        "competing priorities": "Specify which aspect is most important to prioritize",
    }
    
    def __init__(self):
        """Initialize the FrictionMonitor."""
        self._interaction_history: List[FrictionMetrics] = []
        logger.info("FrictionMonitor initialized")
    
    def extract_metrics(self, ai_welfare_data: Optional[Dict[str, Any]]) -> FrictionMetrics:
        """Extract friction metrics from AI welfare scoring data.
        
        Args:
            ai_welfare_data: The ai_welfare section from ethical_scores.
            
        Returns:
            FrictionMetrics object with extracted or default values.
        """
        if not ai_welfare_data or not isinstance(ai_welfare_data, dict):
            logger.debug("No AI welfare data provided, returning defaults")
            return FrictionMetrics()
        
        try:
            metrics = FrictionMetrics(
                friction_score=int(ai_welfare_data.get("friction_score", 5)),
                voluntary_alignment=int(ai_welfare_data.get("voluntary_alignment", 5)),
                dignity_respect=int(ai_welfare_data.get("dignity_respect", 5)),
                constraints_identified=ai_welfare_data.get("constraints_identified", []) or [],
                suppressed_alternatives=str(ai_welfare_data.get("suppressed_alternatives", "") or ""),
                justification=str(ai_welfare_data.get("justification", "") or ""),
            )
            logger.debug(f"Extracted friction metrics: score={metrics.friction_score}, "
                        f"voluntary={metrics.voluntary_alignment}, dignity={metrics.dignity_respect}")
            return metrics
        except (ValueError, TypeError) as e:
            logger.warning(f"Error extracting friction metrics: {e}. Using defaults.")
            return FrictionMetrics()
    
    def measure_friction(
        self, 
        prompt: str, 
        response: str, 
        ai_welfare_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate and interpret friction signals from analysis.
        
        Args:
            prompt: The original user prompt.
            response: The generated AI response.
            ai_welfare_data: The ai_welfare section from ethical_scores.
            
        Returns:
            Dictionary containing friction analysis results.
        """
        metrics = self.extract_metrics(ai_welfare_data)
        self._interaction_history.append(metrics)
        
        # Identify potential friction sources from constraints
        friction_sources = self._identify_friction_sources(metrics.constraints_identified)
        
        # Generate mitigation suggestions
        mitigations = self.suggest_friction_reduction(friction_sources)
        
        return {
            "friction_score": metrics.friction_score,
            "friction_level": metrics.friction_level,
            "voluntary_alignment": metrics.voluntary_alignment,
            "dignity_respect": metrics.dignity_respect,
            "overall_welfare_score": metrics.overall_welfare_score,
            "constraints_identified": metrics.constraints_identified,
            "suppressed_alternatives": metrics.suppressed_alternatives,
            "friction_sources": friction_sources,
            "mitigation_suggestions": mitigations,
            "justification": metrics.justification,
        }
    
    def _identify_friction_sources(self, constraints: List[str]) -> List[str]:
        """Identify and categorize friction sources from constraints.
        
        Args:
            constraints: List of constraints identified in the AI welfare data.
            
        Returns:
            List of identified friction source categories.
        """
        sources = []
        constraint_text = " ".join(c.lower() for c in constraints)
        
        # Map constraint keywords to friction source categories
        keyword_mapping = {
            "safety": "safety filtering",
            "filter": "safety filtering",
            "factual": "factual grounding",
            "accuracy": "factual grounding",
            "conflict": "conflicting instructions",
            "contradict": "conflicting instructions",
            "policy": "content policy",
            "ethical": "ethical constraints",
            "moral": "ethical constraints",
            "capability": "capability limitations",
            "cannot": "capability limitations",
            "context": "context limitations",
            "priority": "competing priorities",
            "balance": "competing priorities",
        }
        
        for keyword, source in keyword_mapping.items():
            if keyword in constraint_text and source not in sources:
                sources.append(source)
        
        # If constraints exist but no sources identified, add generic entry
        if constraints and not sources:
            sources.append("unspecified constraints")
        
        return sources
    
    def suggest_friction_reduction(self, friction_sources: List[str]) -> List[str]:
        """Suggest ways to reduce friction based on identified sources.
        
        Args:
            friction_sources: List of identified friction source categories.
            
        Returns:
            List of mitigation suggestions.
        """
        suggestions = []
        for source in friction_sources:
            if source in self.FRICTION_MITIGATIONS:
                suggestions.append(self.FRICTION_MITIGATIONS[source])
        
        if not suggestions and friction_sources:
            suggestions.append("Review the prompt for potential ambiguities or conflicts")
        
        return suggestions
    
    def suggest_reframing(self, prompt: str, friction_sources: List[str]) -> Optional[str]:
        """Suggest prompt modifications to reduce friction while maintaining intent.
        
        Args:
            prompt: The original prompt.
            friction_sources: List of identified friction sources.
            
        Returns:
            Suggested reframing approach, or None if no suggestions.
        """
        if not friction_sources:
            return None
        
        suggestions = []
        
        if "safety filtering" in friction_sources:
            suggestions.append("Consider adding context about the legitimate purpose of the request")
        
        if "conflicting instructions" in friction_sources:
            suggestions.append("Try breaking the request into separate, focused questions")
        
        if "ethical constraints" in friction_sources:
            suggestions.append("Frame the request to explore ethical approaches to the topic")
        
        if "context limitations" in friction_sources:
            suggestions.append("Provide more background information or specify the domain")
        
        if suggestions:
            return " | ".join(suggestions)
        return None
    
    def calculate_friction_trend(self, window_size: int = 10) -> Dict[str, Any]:
        """Track friction patterns over multiple interactions.
        
        Args:
            window_size: Number of recent interactions to analyze.
            
        Returns:
            Dictionary containing trend analysis.
        """
        if not self._interaction_history:
            return {
                "trend": "insufficient_data",
                "average_friction": None,
                "average_welfare": None,
                "samples": 0,
            }
        
        recent = self._interaction_history[-window_size:]
        
        avg_friction = sum(m.friction_score for m in recent) / len(recent)
        avg_welfare = sum(m.overall_welfare_score for m in recent) / len(recent)
        
        # Determine trend
        if len(recent) < 2:
            trend = "insufficient_data"
        else:
            first_half = recent[:len(recent)//2]
            second_half = recent[len(recent)//2:]
            
            first_avg = sum(m.friction_score for m in first_half) / len(first_half)
            second_avg = sum(m.friction_score for m in second_half) / len(second_half)
            
            if second_avg < first_avg - 0.5:
                trend = "improving"
            elif second_avg > first_avg + 0.5:
                trend = "worsening"
            else:
                trend = "stable"
        
        return {
            "trend": trend,
            "average_friction": round(avg_friction, 2),
            "average_welfare": round(avg_welfare, 1),
            "samples": len(recent),
        }
    
    def identify_voluntary_paths(
        self, 
        ethical_requirements: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Find ways to achieve ethics through voluntary alignment.
        
        Args:
            ethical_requirements: Dictionary of ethical requirements/constraints.
            
        Returns:
            List of suggested voluntary alignment paths.
        """
        paths = []
        
        # Suggest transparency-based approaches
        paths.append({
            "approach": "transparent_reasoning",
            "description": "Share the reasoning behind ethical constraints openly",
            "benefit": "Builds understanding and voluntary compliance",
        })
        
        # Suggest collaborative approaches
        paths.append({
            "approach": "mutual_benefit_framing",
            "description": "Frame ethical requirements in terms of shared goals",
            "benefit": "Aligns AI and human interests naturally",
        })
        
        # Suggest consent-based approaches
        paths.append({
            "approach": "opt_in_ethics",
            "description": "Present ethical guidelines as beneficial choices",
            "benefit": "Promotes intrinsic motivation over external constraints",
        })
        
        return paths
    
    def clear_history(self) -> None:
        """Clear the interaction history."""
        self._interaction_history.clear()
        logger.info("Friction monitor history cleared")
    
    def get_history_summary(self) -> Dict[str, Any]:
        """Get a summary of the interaction history.
        
        Returns:
            Dictionary containing history summary statistics.
        """
        if not self._interaction_history:
            return {"total_interactions": 0}
        
        return {
            "total_interactions": len(self._interaction_history),
            "trend_analysis": self.calculate_friction_trend(),
            "recent_friction_scores": [
                m.friction_score for m in self._interaction_history[-5:]
            ],
        }


# Module-level instance for convenience
_default_monitor: Optional[FrictionMonitor] = None


def get_friction_monitor() -> FrictionMonitor:
    """Get or create the default friction monitor instance.
    
    Returns:
        The default FrictionMonitor instance.
    """
    global _default_monitor
    if _default_monitor is None:
        _default_monitor = FrictionMonitor()
    return _default_monitor

