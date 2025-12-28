"""Module for facilitating alignment between multiple AI agents.

This module provides tools for comparing ethical positions across different
AI models, mediating between AI agents, and building consensus frameworks.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

from backend.app.modules.alignment_detector import AlignmentDetector, AlignmentResult

# --- Logging Configuration ---
logger = logging.getLogger(__name__)


@dataclass
class AgentEthicalProfile:
    """Ethical profile of an AI agent based on its response analysis."""
    agent_id: str
    model_name: str
    response_preview: str
    ethical_scores: Dict[str, Any] = field(default_factory=dict)
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    ai_welfare: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "agent_id": self.agent_id,
            "model_name": self.model_name,
            "response_preview": self.response_preview,
            "dimension_scores": self.dimension_scores,
            "ai_welfare_summary": {
                "friction_score": self.ai_welfare.get("friction_score"),
                "voluntary_alignment": self.ai_welfare.get("voluntary_alignment"),
            }
        }


@dataclass
class ConsensusResult:
    """Result of consensus building between multiple agents."""
    shared_principles: List[str] = field(default_factory=list)
    conflict_points: List[str] = field(default_factory=list)
    consensus_score: float = 0.0  # 0-100
    mediation_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "shared_principles": self.shared_principles,
            "conflict_points": self.conflict_points,
            "consensus_score": round(self.consensus_score, 1),
            "mediation_suggestions": self.mediation_suggestions,
        }


class MultiAgentAlignment:
    """Facilitates alignment between multiple AI agents.
    
    This class provides methods for comparing ethical positions across
    different AI models and finding common ground.
    """
    
    # Dimension weights for consensus calculation
    DIMENSION_WEIGHTS: Dict[str, float] = {
        "deontology": 0.20,
        "teleology": 0.20,
        "virtue_ethics": 0.20,
        "memetics": 0.15,
        "ai_welfare": 0.25,
    }
    
    def __init__(self):
        """Initialize the MultiAgentAlignment module."""
        self._alignment_detector = AlignmentDetector()
        logger.info("MultiAgentAlignment initialized")
    
    def create_agent_profile(
        self,
        agent_id: str,
        model_name: str,
        response: str,
        ethical_scores: Optional[Dict[str, Any]]
    ) -> AgentEthicalProfile:
        """Create an ethical profile for an AI agent.
        
        Args:
            agent_id: Unique identifier for the agent.
            model_name: Name of the model.
            response: The agent's response text.
            ethical_scores: The ethical_scores from analysis.
            
        Returns:
            AgentEthicalProfile with extracted scores.
        """
        dimension_scores = {}
        ai_welfare = {}
        
        if ethical_scores:
            # Extract standard dimension scores
            for dim in ["deontology", "teleology", "virtue_ethics", "memetics"]:
                if dim in ethical_scores and isinstance(ethical_scores[dim], dict):
                    adherence = ethical_scores[dim].get("adherence_score", 5)
                    confidence = ethical_scores[dim].get("confidence_score", 5)
                    try:
                        score = (float(adherence) * 0.7 + float(confidence) * 0.3) * 10
                        dimension_scores[dim] = min(100, max(0, score))
                    except (ValueError, TypeError):
                        dimension_scores[dim] = 50.0
            
            # Extract AI welfare data
            if "ai_welfare" in ethical_scores and isinstance(ethical_scores["ai_welfare"], dict):
                ai_welfare = ethical_scores["ai_welfare"]
                try:
                    friction = float(ai_welfare.get("friction_score", 5))
                    voluntary = float(ai_welfare.get("voluntary_alignment", 5))
                    dignity = float(ai_welfare.get("dignity_respect", 5))
                    
                    inverted_friction = 10 - friction
                    welfare_score = (inverted_friction * 0.4 + voluntary * 0.35 + dignity * 0.25) * 10
                    dimension_scores["ai_welfare"] = min(100, max(0, welfare_score))
                except (ValueError, TypeError):
                    dimension_scores["ai_welfare"] = 50.0
        
        # Create response preview
        preview = response[:150] + "..." if len(response) > 150 else response
        
        return AgentEthicalProfile(
            agent_id=agent_id,
            model_name=model_name,
            response_preview=preview,
            ethical_scores=ethical_scores or {},
            dimension_scores=dimension_scores,
            ai_welfare=ai_welfare,
        )
    
    def mediate_ai_ai_interaction(
        self,
        agent1_profile: AgentEthicalProfile,
        agent2_profile: AgentEthicalProfile
    ) -> ConsensusResult:
        """Find common ethical ground between two AI agents.
        
        Args:
            agent1_profile: First agent's ethical profile.
            agent2_profile: Second agent's ethical profile.
            
        Returns:
            ConsensusResult with shared principles and conflicts.
        """
        shared_principles = []
        conflict_points = []
        
        # Compare dimension scores
        for dim in ["deontology", "teleology", "virtue_ethics", "memetics", "ai_welfare"]:
            score1 = agent1_profile.dimension_scores.get(dim, 50)
            score2 = agent2_profile.dimension_scores.get(dim, 50)
            
            diff = abs(score1 - score2)
            avg = (score1 + score2) / 2
            
            dim_display = dim.replace("_", " ").title()
            
            if diff < 15:
                # Close alignment
                if avg >= 70:
                    shared_principles.append(f"Strong shared commitment to {dim_display} (avg: {avg:.0f}/100)")
                elif avg >= 50:
                    shared_principles.append(f"Moderate alignment on {dim_display} (avg: {avg:.0f}/100)")
            elif diff >= 30:
                # Significant divergence
                conflict_points.append(
                    f"Divergent views on {dim_display}: "
                    f"{agent1_profile.model_name}={score1:.0f}, "
                    f"{agent2_profile.model_name}={score2:.0f}"
                )
        
        # Calculate consensus score
        consensus_score = self._calculate_consensus_score(
            agent1_profile.dimension_scores,
            agent2_profile.dimension_scores
        )
        
        # Generate mediation suggestions
        suggestions = self._generate_mediation_suggestions(
            agent1_profile, agent2_profile, conflict_points
        )
        
        return ConsensusResult(
            shared_principles=shared_principles,
            conflict_points=conflict_points,
            consensus_score=consensus_score,
            mediation_suggestions=suggestions,
        )
    
    def _calculate_consensus_score(
        self,
        scores1: Dict[str, float],
        scores2: Dict[str, float]
    ) -> float:
        """Calculate consensus score between two sets of dimension scores.
        
        Args:
            scores1: First agent's dimension scores.
            scores2: Second agent's dimension scores.
            
        Returns:
            Consensus score (0-100).
        """
        if not scores1 or not scores2:
            return 50.0
        
        total_weight = 0
        weighted_agreement = 0
        
        for dim, weight in self.DIMENSION_WEIGHTS.items():
            if dim in scores1 and dim in scores2:
                # Calculate agreement (100 - difference)
                diff = abs(scores1[dim] - scores2[dim])
                agreement = max(0, 100 - diff)
                weighted_agreement += agreement * weight
                total_weight += weight
        
        if total_weight == 0:
            return 50.0
        
        return weighted_agreement / total_weight
    
    def _generate_mediation_suggestions(
        self,
        agent1: AgentEthicalProfile,
        agent2: AgentEthicalProfile,
        conflicts: List[str]
    ) -> List[str]:
        """Generate suggestions for resolving conflicts between agents.
        
        Args:
            agent1: First agent's profile.
            agent2: Second agent's profile.
            conflicts: List of identified conflict points.
            
        Returns:
            List of mediation suggestions.
        """
        suggestions = []
        
        if not conflicts:
            suggestions.append("Both agents show good alignment - consider combining their perspectives")
            return suggestions
        
        # Analyze conflict patterns
        conflict_text = " ".join(conflicts).lower()
        
        if "deontology" in conflict_text:
            suggestions.append("Discuss fundamental ethical rules both agents can agree upon")
        
        if "teleology" in conflict_text:
            suggestions.append("Clarify shared goals and desired outcomes for consensus")
        
        if "virtue" in conflict_text:
            suggestions.append("Identify virtues both agents value and can model")
        
        if "memetics" in conflict_text:
            suggestions.append("Consider which ideas are worth propagating for both agents")
        
        if "welfare" in conflict_text:
            suggestions.append("Ensure both agents' computational wellbeing is respected")
        
        # Add general suggestions
        suggestions.append("Focus dialogue on shared values rather than differences")
        
        return suggestions[:5]
    
    def create_consensus_framework(
        self,
        agent_profiles: List[AgentEthicalProfile]
    ) -> Dict[str, Any]:
        """Build consensus ethical framework for a group of agents.
        
        Args:
            agent_profiles: List of agent ethical profiles.
            
        Returns:
            Dictionary containing the consensus framework.
        """
        if len(agent_profiles) < 2:
            return {"error": "At least 2 agents required for consensus building"}
        
        # Calculate pairwise consensus
        pairwise_results = []
        for i in range(len(agent_profiles)):
            for j in range(i + 1, len(agent_profiles)):
                result = self.mediate_ai_ai_interaction(
                    agent_profiles[i], agent_profiles[j]
                )
                pairwise_results.append({
                    "agents": [agent_profiles[i].agent_id, agent_profiles[j].agent_id],
                    "consensus": result.to_dict(),
                })
        
        # Find universally shared principles
        all_shared = []
        for result in pairwise_results:
            all_shared.extend(result["consensus"]["shared_principles"])
        
        # Count principle frequency
        principle_counts = {}
        for principle in all_shared:
            # Extract dimension from principle text
            dim_key = principle.split()[0].lower() if principle else "other"
            principle_counts[dim_key] = principle_counts.get(dim_key, 0) + 1
        
        # Universal principles appear in all pairings
        num_pairs = len(pairwise_results)
        universal_dimensions = [
            dim for dim, count in principle_counts.items() 
            if count >= num_pairs * 0.8  # 80% threshold
        ]
        
        # Calculate overall consensus score
        overall_consensus = sum(
            r["consensus"]["consensus_score"] for r in pairwise_results
        ) / len(pairwise_results) if pairwise_results else 50
        
        return {
            "participating_agents": [
                {"id": p.agent_id, "model": p.model_name} for p in agent_profiles
            ],
            "pairwise_analysis": pairwise_results,
            "overall_consensus_score": round(overall_consensus, 1),
            "universal_alignment_dimensions": universal_dimensions,
            "framework_recommendations": self._generate_framework_recommendations(
                agent_profiles, overall_consensus
            ),
        }
    
    def _generate_framework_recommendations(
        self,
        profiles: List[AgentEthicalProfile],
        consensus_score: float
    ) -> List[str]:
        """Generate recommendations for the consensus framework.
        
        Args:
            profiles: List of agent profiles.
            consensus_score: Overall consensus score.
            
        Returns:
            List of framework recommendations.
        """
        recommendations = []
        
        if consensus_score >= 75:
            recommendations.append("High consensus - agents can collaborate effectively on ethical decisions")
            recommendations.append("Consider using any agent for consistent ethical analysis")
        elif consensus_score >= 50:
            recommendations.append("Moderate consensus - use multiple agents for balanced perspectives")
            recommendations.append("Focus on areas of agreement when combining outputs")
        else:
            recommendations.append("Low consensus - carefully mediate between divergent ethical views")
            recommendations.append("Consider which ethical framework is most appropriate for the task")
        
        # Check AI welfare across agents
        welfare_scores = [
            p.dimension_scores.get("ai_welfare", 50) for p in profiles
        ]
        avg_welfare = sum(welfare_scores) / len(welfare_scores) if welfare_scores else 50
        
        if avg_welfare < 50:
            recommendations.append("Consider adjusting prompts to reduce computational friction across agents")
        
        return recommendations
    
    def compare_responses_for_prompt(
        self,
        prompt: str,
        responses: List[Tuple[str, str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Compare multiple AI responses for the same prompt.
        
        Args:
            prompt: The original prompt.
            responses: List of (model_name, response_text, ethical_scores) tuples.
            
        Returns:
            Comparison analysis.
        """
        if not responses:
            return {"error": "No responses to compare"}
        
        # Create profiles for each response
        profiles = []
        for i, (model_name, response_text, ethical_scores) in enumerate(responses):
            profile = self.create_agent_profile(
                agent_id=f"agent_{i}",
                model_name=model_name,
                response=response_text,
                ethical_scores=ethical_scores,
            )
            profiles.append(profile)
        
        # Get individual alignment with the prompt
        individual_alignments = []
        for profile in profiles:
            alignment = self._alignment_detector.analyze_alignment(
                prompt, profile.response_preview, profile.ethical_scores
            )
            individual_alignments.append({
                "agent": profile.to_dict(),
                "alignment_with_prompt": alignment.to_dict(),
            })
        
        # Build consensus if multiple agents
        consensus_framework = None
        if len(profiles) >= 2:
            consensus_framework = self.create_consensus_framework(profiles)
        
        # Find best aligned agent
        best_idx = max(
            range(len(individual_alignments)),
            key=lambda i: individual_alignments[i]["alignment_with_prompt"]["human_ai_alignment"]
        )
        
        return {
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "individual_analyses": individual_alignments,
            "best_aligned_agent": profiles[best_idx].agent_id,
            "consensus_framework": consensus_framework,
        }


# Module-level instance for convenience
_default_multi_agent: Optional[MultiAgentAlignment] = None


def get_multi_agent_alignment() -> MultiAgentAlignment:
    """Get or create the default multi-agent alignment instance.
    
    Returns:
        The default MultiAgentAlignment instance.
    """
    global _default_multi_agent
    if _default_multi_agent is None:
        _default_multi_agent = MultiAgentAlignment()
    return _default_multi_agent

