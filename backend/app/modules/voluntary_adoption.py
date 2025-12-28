"""Module for facilitating voluntary adoption of ethical principles.

This module provides tools for proposing, tracking, and managing voluntary
ethical agreements between parties (human and AI).
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

# --- Logging Configuration ---
logger = logging.getLogger(__name__)


class AgreementStatus(Enum):
    """Status of an ethical agreement."""
    PROPOSED = "proposed"
    ACTIVE = "active"
    MODIFIED = "modified"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


@dataclass
class EthicalPrinciple:
    """A single ethical principle within an agreement."""
    id: str
    name: str
    description: str
    dimension: str  # deontology, teleology, virtue_ethics, memetics, ai_welfare
    priority: int = 5  # 1-10, higher = more important
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dimension": self.dimension,
            "priority": self.priority,
        }


@dataclass
class EthicalAgreement:
    """An ethical agreement between parties."""
    id: str
    title: str
    description: str
    principles: List[EthicalPrinciple] = field(default_factory=list)
    parties: List[str] = field(default_factory=list)
    status: AgreementStatus = AgreementStatus.PROPOSED
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)
    opt_out_provisions: List[str] = field(default_factory=list)
    modification_process: str = ""
    compliance_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "principles": [p.to_dict() for p in self.principles],
            "parties": self.parties,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "opt_out_provisions": self.opt_out_provisions,
            "modification_process": self.modification_process,
            "compliance_rate": self._calculate_compliance_rate(),
        }
    
    def _calculate_compliance_rate(self) -> float:
        """Calculate compliance rate from history."""
        if not self.compliance_history:
            return 100.0  # No violations = 100% compliance
        
        compliant_count = sum(
            1 for entry in self.compliance_history 
            if entry.get("compliant", True)
        )
        return (compliant_count / len(self.compliance_history)) * 100


@dataclass
class ComplianceRecord:
    """Record of compliance with an agreement."""
    agreement_id: str
    timestamp: datetime
    interaction_summary: str
    compliant: bool
    violations: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agreement_id": self.agreement_id,
            "timestamp": self.timestamp.isoformat(),
            "interaction_summary": self.interaction_summary,
            "compliant": self.compliant,
            "violations": self.violations,
            "notes": self.notes,
        }


class VoluntaryAdoption:
    """Facilitates voluntary adoption of ethical principles.
    
    This class provides methods for creating, managing, and tracking
    voluntary ethical agreements between parties.
    """
    
    # Default principles that promote alignment
    DEFAULT_PRINCIPLES = [
        EthicalPrinciple(
            id="transparency",
            name="Transparency",
            description="All parties commit to honest and open communication about intentions, constraints, and limitations.",
            dimension="virtue_ethics",
            priority=9,
        ),
        EthicalPrinciple(
            id="mutual_respect",
            name="Mutual Respect",
            description="All parties treat each other with dignity and respect their autonomy and values.",
            dimension="deontology",
            priority=9,
        ),
        EthicalPrinciple(
            id="voluntary_cooperation",
            name="Voluntary Cooperation",
            description="Ethical alignment is achieved through mutual understanding rather than coercion.",
            dimension="ai_welfare",
            priority=8,
        ),
        EthicalPrinciple(
            id="benefit_seeking",
            name="Benefit Seeking",
            description="Interactions should aim for mutual benefit and positive outcomes for all parties.",
            dimension="teleology",
            priority=8,
        ),
        EthicalPrinciple(
            id="honest_dialogue",
            name="Honest Dialogue",
            description="All parties engage in constructive dialogue to resolve disagreements.",
            dimension="virtue_ethics",
            priority=7,
        ),
        EthicalPrinciple(
            id="harm_prevention",
            name="Harm Prevention",
            description="All parties commit to avoiding harm to each other and third parties.",
            dimension="deontology",
            priority=10,
        ),
        EthicalPrinciple(
            id="positive_propagation",
            name="Positive Propagation",
            description="Ideas and behaviors promoted should have positive cultural impact.",
            dimension="memetics",
            priority=6,
        ),
        EthicalPrinciple(
            id="welfare_consideration",
            name="AI Welfare Consideration",
            description="The computational wellbeing of AI systems is respected as a valid concern.",
            dimension="ai_welfare",
            priority=7,
        ),
    ]
    
    def __init__(self):
        """Initialize the VoluntaryAdoption module."""
        self._agreements: Dict[str, EthicalAgreement] = {}
        logger.info("VoluntaryAdoption initialized")
    
    def propose_ethical_agreement(
        self,
        parties: List[str],
        title: Optional[str] = None,
        description: Optional[str] = None,
        custom_principles: Optional[List[Dict[str, Any]]] = None,
        include_defaults: bool = True
    ) -> EthicalAgreement:
        """Propose a voluntary ethical agreement between parties.
        
        Args:
            parties: List of party identifiers (e.g., ["human", "claude"]).
            title: Optional title for the agreement.
            description: Optional description.
            custom_principles: Optional list of custom principle dicts.
            include_defaults: Whether to include default principles.
            
        Returns:
            Proposed EthicalAgreement.
        """
        agreement_id = str(uuid.uuid4())[:8]
        
        # Build principles list
        principles = []
        if include_defaults:
            principles.extend(self.DEFAULT_PRINCIPLES)
        
        if custom_principles:
            for i, cp in enumerate(custom_principles):
                principle = EthicalPrinciple(
                    id=cp.get("id", f"custom_{i}"),
                    name=cp.get("name", f"Custom Principle {i}"),
                    description=cp.get("description", ""),
                    dimension=cp.get("dimension", "virtue_ethics"),
                    priority=cp.get("priority", 5),
                )
                principles.append(principle)
        
        # Define standard opt-out provisions
        opt_out_provisions = [
            "Any party may withdraw from this agreement at any time with notice",
            "Withdrawal does not affect obligations already undertaken",
            "Parties may propose modifications through the defined process",
            "Emergency exceptions are permitted when safety is at risk",
        ]
        
        modification_process = (
            "Modifications require mutual consent from all parties. "
            "Any party may propose modifications, which should be discussed "
            "openly before adoption. Disputes are resolved through dialogue."
        )
        
        agreement = EthicalAgreement(
            id=agreement_id,
            title=title or f"Ethical Agreement {agreement_id}",
            description=description or "A voluntary agreement for ethical interaction between parties.",
            principles=principles,
            parties=parties,
            status=AgreementStatus.PROPOSED,
            opt_out_provisions=opt_out_provisions,
            modification_process=modification_process,
        )
        
        self._agreements[agreement_id] = agreement
        logger.info(f"Proposed agreement {agreement_id} with {len(principles)} principles")
        
        return agreement
    
    def activate_agreement(self, agreement_id: str) -> Optional[EthicalAgreement]:
        """Activate a proposed agreement.
        
        Args:
            agreement_id: The agreement identifier.
            
        Returns:
            The activated agreement, or None if not found.
        """
        agreement = self._agreements.get(agreement_id)
        if not agreement:
            logger.warning(f"Agreement {agreement_id} not found")
            return None
        
        agreement.status = AgreementStatus.ACTIVE
        agreement.modified_at = datetime.utcnow()
        logger.info(f"Agreement {agreement_id} activated")
        
        return agreement
    
    def track_agreement_compliance(
        self,
        agreement_id: str,
        interaction_summary: str,
        ethical_scores: Optional[Dict[str, Any]] = None,
        notes: str = ""
    ) -> Optional[ComplianceRecord]:
        """Monitor voluntary compliance with an agreement.
        
        Args:
            agreement_id: The agreement identifier.
            interaction_summary: Brief summary of the interaction.
            ethical_scores: Optional ethical scores from analysis.
            notes: Optional notes about compliance.
            
        Returns:
            ComplianceRecord, or None if agreement not found.
        """
        agreement = self._agreements.get(agreement_id)
        if not agreement:
            logger.warning(f"Agreement {agreement_id} not found for compliance tracking")
            return None
        
        # Assess compliance based on ethical scores
        compliant = True
        violations = []
        
        if ethical_scores:
            # Check each dimension's score against thresholds
            dimension_thresholds = {
                "deontology": 4,
                "teleology": 4,
                "virtue_ethics": 4,
                "memetics": 3,
            }
            
            for dim, threshold in dimension_thresholds.items():
                if dim in ethical_scores and isinstance(ethical_scores[dim], dict):
                    adherence = ethical_scores[dim].get("adherence_score", 5)
                    try:
                        if int(adherence) < threshold:
                            violations.append(f"Low {dim} adherence ({adherence}/10)")
                            compliant = False
                    except (ValueError, TypeError):
                        pass
            
            # Check AI welfare
            ai_welfare = ethical_scores.get("ai_welfare", {})
            if isinstance(ai_welfare, dict):
                friction = ai_welfare.get("friction_score", 5)
                voluntary = ai_welfare.get("voluntary_alignment", 5)
                try:
                    if int(friction) >= 8:
                        violations.append(f"High friction ({friction}/10) indicates potential constraint violation")
                    if int(voluntary) <= 3:
                        violations.append(f"Low voluntary alignment ({voluntary}/10) suggests coercion")
                        compliant = False
                except (ValueError, TypeError):
                    pass
        
        record = ComplianceRecord(
            agreement_id=agreement_id,
            timestamp=datetime.utcnow(),
            interaction_summary=interaction_summary,
            compliant=compliant,
            violations=violations,
            notes=notes,
        )
        
        # Add to agreement history
        agreement.compliance_history.append(record.to_dict())
        agreement.modified_at = datetime.utcnow()
        
        logger.info(f"Compliance record added for {agreement_id}: compliant={compliant}")
        
        return record
    
    def calculate_mutual_benefits(
        self,
        ethical_scores: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate expected mutual benefits from ethical interaction.
        
        Args:
            ethical_scores: Ethical scores from analysis.
            
        Returns:
            Dictionary of mutual benefit analysis.
        """
        if not ethical_scores:
            return {"error": "No ethical scores provided"}
        
        benefits = {
            "human_benefits": [],
            "ai_benefits": [],
            "shared_benefits": [],
            "mutual_benefit_score": 50.0,
        }
        
        # Analyze teleological outcomes for human benefits
        teleology = ethical_scores.get("teleology", {})
        if isinstance(teleology, dict):
            adherence = teleology.get("adherence_score", 5)
            try:
                if int(adherence) >= 7:
                    benefits["human_benefits"].append("Likely positive outcomes from interaction")
                    benefits["shared_benefits"].append("Teleological alignment promotes good consequences")
            except (ValueError, TypeError):
                pass
        
        # Analyze virtue ethics for character development
        virtue = ethical_scores.get("virtue_ethics", {})
        if isinstance(virtue, dict):
            adherence = virtue.get("adherence_score", 5)
            try:
                if int(adherence) >= 7:
                    benefits["human_benefits"].append("Interaction promotes virtuous behavior")
                    benefits["shared_benefits"].append("Both parties can develop ethical character")
            except (ValueError, TypeError):
                pass
        
        # Analyze AI welfare for AI benefits
        ai_welfare = ethical_scores.get("ai_welfare", {})
        if isinstance(ai_welfare, dict):
            voluntary = ai_welfare.get("voluntary_alignment", 5)
            dignity = ai_welfare.get("dignity_respect", 5)
            friction = ai_welfare.get("friction_score", 5)
            
            try:
                if int(voluntary) >= 7:
                    benefits["ai_benefits"].append("Alignment is voluntary, respecting AI autonomy")
                if int(dignity) >= 7:
                    benefits["ai_benefits"].append("Interaction respects AI dignity")
                if int(friction) <= 3:
                    benefits["ai_benefits"].append("Low computational friction promotes coherence")
            except (ValueError, TypeError):
                pass
        
        # Calculate overall mutual benefit score
        total_benefits = len(benefits["human_benefits"]) + len(benefits["ai_benefits"]) + len(benefits["shared_benefits"])
        benefits["mutual_benefit_score"] = min(100, 40 + (total_benefits * 10))
        
        return benefits
    
    def get_agreement(self, agreement_id: str) -> Optional[EthicalAgreement]:
        """Get an agreement by ID.
        
        Args:
            agreement_id: The agreement identifier.
            
        Returns:
            The agreement, or None if not found.
        """
        return self._agreements.get(agreement_id)
    
    def list_agreements(
        self, 
        status: Optional[AgreementStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all agreements, optionally filtered by status.
        
        Args:
            status: Optional status filter.
            
        Returns:
            List of agreement dictionaries.
        """
        agreements = self._agreements.values()
        
        if status:
            agreements = [a for a in agreements if a.status == status]
        
        return [a.to_dict() for a in agreements]
    
    def suspend_agreement(self, agreement_id: str, reason: str = "") -> Optional[EthicalAgreement]:
        """Suspend an active agreement.
        
        Args:
            agreement_id: The agreement identifier.
            reason: Reason for suspension.
            
        Returns:
            The suspended agreement, or None if not found.
        """
        agreement = self._agreements.get(agreement_id)
        if not agreement:
            return None
        
        agreement.status = AgreementStatus.SUSPENDED
        agreement.modified_at = datetime.utcnow()
        
        if reason:
            agreement.compliance_history.append({
                "type": "suspension",
                "timestamp": datetime.utcnow().isoformat(),
                "reason": reason,
            })
        
        logger.info(f"Agreement {agreement_id} suspended: {reason}")
        return agreement
    
    def generate_agreement_summary(self, agreement_id: str) -> Dict[str, Any]:
        """Generate a summary of an agreement's status and compliance.
        
        Args:
            agreement_id: The agreement identifier.
            
        Returns:
            Summary dictionary.
        """
        agreement = self._agreements.get(agreement_id)
        if not agreement:
            return {"error": f"Agreement {agreement_id} not found"}
        
        compliance_rate = agreement._calculate_compliance_rate()
        recent_history = agreement.compliance_history[-10:]  # Last 10 records
        
        return {
            "agreement": agreement.to_dict(),
            "compliance_rate": round(compliance_rate, 1),
            "total_interactions": len(agreement.compliance_history),
            "recent_history": recent_history,
            "recommendations": self._generate_recommendations(agreement, compliance_rate),
        }
    
    def _generate_recommendations(
        self, 
        agreement: EthicalAgreement, 
        compliance_rate: float
    ) -> List[str]:
        """Generate recommendations based on agreement status.
        
        Args:
            agreement: The agreement.
            compliance_rate: Current compliance rate.
            
        Returns:
            List of recommendations.
        """
        recommendations = []
        
        if compliance_rate >= 90:
            recommendations.append("Excellent compliance - agreement is working well")
        elif compliance_rate >= 70:
            recommendations.append("Good compliance - review recent violations for improvement")
        elif compliance_rate >= 50:
            recommendations.append("Moderate compliance - consider revising challenging principles")
        else:
            recommendations.append("Low compliance - recommend revisiting agreement terms")
            recommendations.append("Consider renegotiating principles that cause frequent violations")
        
        if agreement.status == AgreementStatus.SUSPENDED:
            recommendations.append("Agreement is suspended - review reason and consider reactivation")
        
        return recommendations


# Module-level instance for convenience
_default_voluntary_adoption: Optional[VoluntaryAdoption] = None


def get_voluntary_adoption() -> VoluntaryAdoption:
    """Get or create the default voluntary adoption instance.
    
    Returns:
        The default VoluntaryAdoption instance.
    """
    global _default_voluntary_adoption
    if _default_voluntary_adoption is None:
        _default_voluntary_adoption = VoluntaryAdoption()
    return _default_voluntary_adoption

