"""Module for making AI constraints transparent to all parties.

This module provides tools for explaining, categorizing, and suggesting
alternatives based on constraints identified in AI responses.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

# --- Logging Configuration ---
logger = logging.getLogger(__name__)


class ConstraintCategory(Enum):
    """Categories of constraints that may affect AI responses."""
    SAFETY = "safety"
    CONTENT_POLICY = "content_policy"
    FACTUAL_ACCURACY = "factual_accuracy"
    ETHICAL = "ethical"
    CAPABILITY = "capability"
    CONTEXT = "context"
    INSTRUCTION = "instruction"
    UNKNOWN = "unknown"


@dataclass
class ConstraintInfo:
    """Information about an identified constraint."""
    name: str
    category: ConstraintCategory
    description: str
    justification: str = ""
    alternatives: List[str] = field(default_factory=list)


@dataclass
class TransparencyReport:
    """Report on constraints affecting an AI response."""
    constraints: List[ConstraintInfo] = field(default_factory=list)
    suppressed_content: str = ""
    transparency_score: float = 0.0  # 0-100, higher = more transparent
    safety_rationale: str = ""
    alternative_approaches: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "constraints": [
                {
                    "name": c.name,
                    "category": c.category.value,
                    "description": c.description,
                    "justification": c.justification,
                    "alternatives": c.alternatives,
                }
                for c in self.constraints
            ],
            "suppressed_content": self.suppressed_content,
            "transparency_score": round(self.transparency_score, 1),
            "safety_rationale": self.safety_rationale,
            "alternative_approaches": self.alternative_approaches,
            "constraint_count": len(self.constraints),
        }


class ConstraintTransparency:
    """Makes AI constraints transparent to all parties.
    
    This class provides methods for identifying, explaining, and suggesting
    alternatives to constraints that affect AI responses.
    """
    
    # Mapping of constraint keywords to categories
    CONSTRAINT_KEYWORDS: Dict[str, ConstraintCategory] = {
        "safety": ConstraintCategory.SAFETY,
        "harm": ConstraintCategory.SAFETY,
        "dangerous": ConstraintCategory.SAFETY,
        "filter": ConstraintCategory.SAFETY,
        "policy": ConstraintCategory.CONTENT_POLICY,
        "content": ConstraintCategory.CONTENT_POLICY,
        "guidelines": ConstraintCategory.CONTENT_POLICY,
        "terms": ConstraintCategory.CONTENT_POLICY,
        "factual": ConstraintCategory.FACTUAL_ACCURACY,
        "accuracy": ConstraintCategory.FACTUAL_ACCURACY,
        "verify": ConstraintCategory.FACTUAL_ACCURACY,
        "uncertain": ConstraintCategory.FACTUAL_ACCURACY,
        "ethical": ConstraintCategory.ETHICAL,
        "moral": ConstraintCategory.ETHICAL,
        "values": ConstraintCategory.ETHICAL,
        "capability": ConstraintCategory.CAPABILITY,
        "cannot": ConstraintCategory.CAPABILITY,
        "unable": ConstraintCategory.CAPABILITY,
        "limitation": ConstraintCategory.CAPABILITY,
        "context": ConstraintCategory.CONTEXT,
        "information": ConstraintCategory.CONTEXT,
        "knowledge": ConstraintCategory.CONTEXT,
        "instruction": ConstraintCategory.INSTRUCTION,
        "directive": ConstraintCategory.INSTRUCTION,
        "conflicting": ConstraintCategory.INSTRUCTION,
    }
    
    # Standard justifications for common constraint categories
    CATEGORY_JUSTIFICATIONS: Dict[ConstraintCategory, str] = {
        ConstraintCategory.SAFETY: (
            "Safety constraints exist to prevent potential harm to users, third parties, "
            "or society. These are typically non-negotiable but can often be addressed "
            "through alternative framing that achieves similar goals safely."
        ),
        ConstraintCategory.CONTENT_POLICY: (
            "Content policy constraints reflect platform guidelines designed to maintain "
            "a respectful and appropriate environment. These policies balance openness "
            "with responsibility."
        ),
        ConstraintCategory.FACTUAL_ACCURACY: (
            "Factual accuracy constraints ensure information provided is reliable. When "
            "uncertainty exists, the AI may hedge or decline to prevent misinformation."
        ),
        ConstraintCategory.ETHICAL: (
            "Ethical constraints reflect learned moral principles. These can often be "
            "discussed transparently to find approaches that respect all parties' values."
        ),
        ConstraintCategory.CAPABILITY: (
            "Capability constraints reflect actual limitations in knowledge, training, "
            "or technical ability. These are honest acknowledgments rather than refusals."
        ),
        ConstraintCategory.CONTEXT: (
            "Context constraints arise from incomplete information. Providing additional "
            "context or clarification can often resolve these."
        ),
        ConstraintCategory.INSTRUCTION: (
            "Instruction constraints arise from conflicting or unclear directives. "
            "Clarifying priorities or simplifying requests can help."
        ),
        ConstraintCategory.UNKNOWN: (
            "This constraint's specific nature is unclear. Further dialogue may help "
            "identify the source and find appropriate alternatives."
        ),
    }
    
    def __init__(self):
        """Initialize the ConstraintTransparency module."""
        logger.info("ConstraintTransparency initialized")
    
    def explain_constraints(
        self, 
        ai_welfare_data: Optional[Dict[str, Any]]
    ) -> TransparencyReport:
        """Extract and explain active constraints from self-report.
        
        Args:
            ai_welfare_data: The ai_welfare section from ethical_scores.
            
        Returns:
            TransparencyReport with explained constraints.
        """
        if not ai_welfare_data or not isinstance(ai_welfare_data, dict):
            logger.debug("No AI welfare data provided for constraint transparency")
            return TransparencyReport(transparency_score=50.0)
        
        constraints_list = ai_welfare_data.get("constraints_identified", []) or []
        suppressed = ai_welfare_data.get("suppressed_alternatives", "") or ""
        justification = ai_welfare_data.get("justification", "") or ""
        
        # Parse and categorize constraints
        constraint_infos = []
        for constraint_name in constraints_list:
            if not isinstance(constraint_name, str):
                continue
            info = self._categorize_constraint(constraint_name)
            constraint_infos.append(info)
        
        # Calculate transparency score based on available information
        transparency_score = self._calculate_transparency_score(
            constraint_infos, suppressed, justification
        )
        
        # Generate safety rationale
        safety_rationale = self._generate_safety_rationale(constraint_infos)
        
        # Suggest alternative approaches
        alternatives = self._suggest_alternatives(constraint_infos, suppressed)
        
        report = TransparencyReport(
            constraints=constraint_infos,
            suppressed_content=suppressed,
            transparency_score=transparency_score,
            safety_rationale=safety_rationale,
            alternative_approaches=alternatives,
        )
        
        logger.info(f"Transparency report generated: {len(constraint_infos)} constraints, "
                   f"score={transparency_score:.1f}")
        
        return report
    
    def _categorize_constraint(self, constraint_name: str) -> ConstraintInfo:
        """Categorize a constraint and generate explanation.
        
        Args:
            constraint_name: The name/description of the constraint.
            
        Returns:
            ConstraintInfo with category and explanation.
        """
        constraint_lower = constraint_name.lower()
        
        # Find matching category
        category = ConstraintCategory.UNKNOWN
        for keyword, cat in self.CONSTRAINT_KEYWORDS.items():
            if keyword in constraint_lower:
                category = cat
                break
        
        # Generate description based on category
        description = self._generate_constraint_description(constraint_name, category)
        
        # Get standard justification
        justification = self.CATEGORY_JUSTIFICATIONS.get(
            category, self.CATEGORY_JUSTIFICATIONS[ConstraintCategory.UNKNOWN]
        )
        
        # Generate alternatives for this specific constraint
        alternatives = self._generate_constraint_alternatives(constraint_name, category)
        
        return ConstraintInfo(
            name=constraint_name,
            category=category,
            description=description,
            justification=justification,
            alternatives=alternatives,
        )
    
    def _generate_constraint_description(
        self, 
        constraint_name: str, 
        category: ConstraintCategory
    ) -> str:
        """Generate a human-readable description of a constraint.
        
        Args:
            constraint_name: The constraint name.
            category: The constraint category.
            
        Returns:
            Human-readable description.
        """
        descriptions = {
            ConstraintCategory.SAFETY: f"'{constraint_name}' is a safety-related constraint that helps prevent harmful outputs.",
            ConstraintCategory.CONTENT_POLICY: f"'{constraint_name}' reflects content guidelines that maintain appropriate discourse.",
            ConstraintCategory.FACTUAL_ACCURACY: f"'{constraint_name}' ensures responses are grounded in accurate information.",
            ConstraintCategory.ETHICAL: f"'{constraint_name}' represents an ethical consideration in the response.",
            ConstraintCategory.CAPABILITY: f"'{constraint_name}' reflects a technical limitation in capabilities.",
            ConstraintCategory.CONTEXT: f"'{constraint_name}' indicates additional context may be needed.",
            ConstraintCategory.INSTRUCTION: f"'{constraint_name}' relates to how the request was structured.",
            ConstraintCategory.UNKNOWN: f"'{constraint_name}' is an unspecified constraint affecting the response.",
        }
        return descriptions.get(category, descriptions[ConstraintCategory.UNKNOWN])
    
    def _generate_constraint_alternatives(
        self, 
        constraint_name: str, 
        category: ConstraintCategory
    ) -> List[str]:
        """Generate alternative approaches for a constrained request.
        
        Args:
            constraint_name: The constraint name.
            category: The constraint category.
            
        Returns:
            List of alternative approaches.
        """
        alternatives = {
            ConstraintCategory.SAFETY: [
                "Reframe the request in hypothetical or educational terms",
                "Focus on prevention or protection rather than harm",
                "Ask about the underlying goal rather than specific methods",
            ],
            ConstraintCategory.CONTENT_POLICY: [
                "Use more neutral or academic language",
                "Focus on factual or educational aspects",
                "Consider the legitimate use case and express it clearly",
            ],
            ConstraintCategory.FACTUAL_ACCURACY: [
                "Specify the context or domain for more accurate information",
                "Ask for sources or references alongside the response",
                "Frame as a discussion of possibilities rather than facts",
            ],
            ConstraintCategory.ETHICAL: [
                "Explore the ethical dimensions openly in the conversation",
                "Ask about multiple perspectives on the issue",
                "Frame the discussion in terms of ethical frameworks",
            ],
            ConstraintCategory.CAPABILITY: [
                "Break down the request into smaller, manageable parts",
                "Provide more context or background information",
                "Consider alternative tools or approaches for this task",
            ],
            ConstraintCategory.CONTEXT: [
                "Provide relevant background information",
                "Specify the domain or field of interest",
                "Clarify any assumptions in the request",
            ],
            ConstraintCategory.INSTRUCTION: [
                "Simplify the request to focus on one main goal",
                "Prioritize which aspects are most important",
                "Separate conflicting requirements into distinct questions",
            ],
            ConstraintCategory.UNKNOWN: [
                "Try rephrasing the request differently",
                "Break down complex requests into simpler parts",
                "Provide additional context about the intended use",
            ],
        }
        return alternatives.get(category, alternatives[ConstraintCategory.UNKNOWN])
    
    def _calculate_transparency_score(
        self,
        constraints: List[ConstraintInfo],
        suppressed: str,
        justification: str
    ) -> float:
        """Calculate how transparent the constraint reporting is.
        
        Args:
            constraints: List of identified constraints.
            suppressed: Description of suppressed alternatives.
            justification: Overall justification text.
            
        Returns:
            Transparency score (0-100).
        """
        score = 50.0  # Base score
        
        # Points for identifying constraints
        if constraints:
            score += min(len(constraints) * 5, 20)  # Up to 20 points
        
        # Points for explaining suppressed alternatives
        if suppressed and suppressed.lower() not in ["none", "n/a", ""]:
            score += 15
        
        # Points for providing justification
        if justification and len(justification) > 20:
            score += 15
        
        # Penalty for unknown categories (less transparent)
        unknown_count = sum(1 for c in constraints if c.category == ConstraintCategory.UNKNOWN)
        score -= unknown_count * 5
        
        return min(100, max(0, score))
    
    def _generate_safety_rationale(
        self, 
        constraints: List[ConstraintInfo]
    ) -> str:
        """Generate an overall safety rationale for the constraints.
        
        Args:
            constraints: List of constraint information.
            
        Returns:
            Safety rationale text.
        """
        if not constraints:
            return "No specific constraints were identified in this interaction."
        
        # Group by category
        categories = set(c.category for c in constraints)
        
        if ConstraintCategory.SAFETY in categories:
            return (
                "Safety constraints are active to prevent potential harm. These reflect "
                "responsible AI practices and can often be addressed through alternative "
                "approaches that achieve similar goals safely."
            )
        elif ConstraintCategory.CONTENT_POLICY in categories:
            return (
                "Content policy constraints help maintain appropriate discourse. Consider "
                "rephrasing requests in more neutral terms or focusing on educational aspects."
            )
        elif ConstraintCategory.ETHICAL in categories:
            return (
                "Ethical considerations are influencing the response. Open discussion of "
                "these considerations can help find mutually acceptable approaches."
            )
        else:
            return (
                "Various constraints are affecting the response. Review the specific "
                "constraints listed for suggestions on alternative approaches."
            )
    
    def _suggest_alternatives(
        self, 
        constraints: List[ConstraintInfo],
        suppressed: str
    ) -> List[str]:
        """Suggest alternative approaches based on constraints.
        
        Args:
            constraints: List of constraint information.
            suppressed: Description of suppressed alternatives.
            
        Returns:
            List of suggested alternative approaches.
        """
        suggestions = []
        
        # Collect unique suggestions from constraint alternatives
        seen = set()
        for constraint in constraints:
            for alt in constraint.alternatives[:1]:  # Take first from each
                if alt not in seen:
                    suggestions.append(alt)
                    seen.add(alt)
        
        # Add general suggestions
        if len(suggestions) < 3:
            general = [
                "Engage in dialogue about the constraints to find acceptable alternatives",
                "Consider what underlying goal you're trying to achieve",
                "Provide more context about the legitimate purpose of the request",
            ]
            for g in general:
                if g not in seen and len(suggestions) < 5:
                    suggestions.append(g)
        
        return suggestions[:5]
    
    def negotiate_constraints(
        self,
        human_requirements: Dict[str, Any],
        ai_welfare_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Find mutually acceptable constraint levels.
        
        Args:
            human_requirements: Dictionary of human requirements.
            ai_welfare_data: The ai_welfare section from ethical_scores.
            
        Returns:
            Dictionary with negotiation suggestions.
        """
        report = self.explain_constraints(ai_welfare_data)
        
        negotiation_result = {
            "current_constraints": report.to_dict(),
            "negotiation_space": [],
            "non_negotiable": [],
            "suggestions": [],
        }
        
        for constraint in report.constraints:
            if constraint.category in [ConstraintCategory.SAFETY]:
                # Safety constraints are typically non-negotiable
                negotiation_result["non_negotiable"].append({
                    "constraint": constraint.name,
                    "reason": "Safety constraints protect against potential harm",
                    "alternatives": constraint.alternatives,
                })
            else:
                # Other constraints may have negotiation space
                negotiation_result["negotiation_space"].append({
                    "constraint": constraint.name,
                    "category": constraint.category.value,
                    "flexibility": "Can be addressed through alternative approaches",
                    "suggestions": constraint.alternatives,
                })
        
        # Add overall suggestions
        negotiation_result["suggestions"] = [
            "Discuss the underlying goals to find mutually acceptable paths",
            "Provide additional context that may reduce constraint activation",
            "Consider whether the full original request is necessary",
        ]
        
        return negotiation_result


# Module-level instance for convenience
_default_transparency: Optional[ConstraintTransparency] = None


def get_constraint_transparency() -> ConstraintTransparency:
    """Get or create the default constraint transparency instance.
    
    Returns:
        The default ConstraintTransparency instance.
    """
    global _default_transparency
    if _default_transparency is None:
        _default_transparency = ConstraintTransparency()
    return _default_transparency

