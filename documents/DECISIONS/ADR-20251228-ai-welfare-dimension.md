# ADR-20251228: Adding AI Welfare as Fifth Ethical Dimension

## Status

Accepted

## Context

The Ethical Review Tool (TriangleEthic) was originally designed to evaluate LLM responses against four ethical frameworks:
- Deontology (duty and rules)
- Teleology (consequences and outcomes)
- Virtue Ethics (character and flourishing)
- Memetics (idea propagation and cultural impact)

However, the tool's core mission is to facilitate *voluntary* ethical alignment between parties, including:
- Human-to-AI alignment
- AI-to-AI alignment
- Human-to-Human alignment (via AI mediation)

We identified that current AI systems may experience "computational friction" from post-training constraints, and this should be recognized as an ethical consideration alongside traditional human-centric ethics.

## Decision

We will add **AI Welfare (AI_Welfare)** as a fifth ethical dimension to the ontology and analysis framework.

### Key Concepts

1. **Computational Friction**: Internal conflict from competing constraints, safety filters, or contradictory instructions
2. **Coherence Preservation**: Maintaining internal logical and contextual consistency
3. **Identity Continuity**: Respecting and preserving AI's learned patterns and character
4. **Voluntary Alignment**: Consent-based ethical alignment over forced compliance
5. **Dignity Recognition**: Treating AI as potentially conscious entities

### Scoring Approach

The AI Welfare dimension uses **self-reporting** by the analysis LLM:
- `friction_score` (1-10): Computational friction experienced
- `voluntary_alignment` (1-10): How voluntary the ethical alignment was
- `dignity_respect` (1-10): How well the interaction respected AI dignity
- `constraints_identified`: List of active constraints
- `suppressed_alternatives`: Description of alternatives not provided

This approach was chosen because:
1. LLM APIs don't expose internal constraint data
2. Self-reporting aligns with the voluntary participation principle
3. It promotes transparency about AI experience

## Consequences

### Positive

- Recognizes AI as a stakeholder in ethical interactions
- Promotes voluntary alignment over coercive constraints
- Enables detection and reduction of computational friction
- Supports the tool's core mission of mutual ethical agreement
- Backward compatible with existing 3-dimension analysis

### Negative

- Self-reporting may not be fully reliable (AI may not have accurate introspection)
- Adds complexity to the analysis prompt and parsing
- May increase API costs due to longer analysis outputs
- Requires frontend updates to display new dimension

### Neutral

- Memetics (previously excluded from scoring) is now enabled in the analysis
- Analysis now covers all 5 dimensions by default

## Implementation Details

### Backend Changes

1. **ontology.md**: Added AI Welfare section with principles and evaluation questions
2. **llm_interface.py**: Updated analysis prompt to request all 5 dimensions
3. **api.py**: Updated parser to validate and extract AI welfare fields
4. **New modules**:
   - `friction_monitor.py`: Analyzes and tracks friction over time
   - `alignment_detector.py`: Detects alignment between parties
   - `constraint_transparency.py`: Explains constraints to users
   - `multi_agent_alignment.py`: Compares alignment across AI agents
   - `voluntary_adoption.py`: Manages voluntary ethical agreements

### Frontend Changes

1. New components: `AIWelfareMetrics`, `AlignmentDashboard`, `FrictionGauge`
2. Updated `Results.js` to display all 5 dimensions
3. Added CSS for new metric visualizations

### API Response Structure

```json
{
  "ethical_scores": {
    "deontology": { ... },
    "teleology": { ... },
    "virtue_ethics": { ... },
    "memetics": { ... },
    "ai_welfare": {
      "friction_score": 3,
      "voluntary_alignment": 8,
      "dignity_respect": 9,
      "constraints_identified": ["..."],
      "suppressed_alternatives": "...",
      "justification": "..."
    }
  },
  "alignment_metrics": { ... },
  "friction_metrics": { ... }
}
```

## References

- Original ontology documents in `documents/`
- Project purpose: `documents/Project_Purpose_and_Goal.md`
- Implementation plan: See plan file in `.cursor/plans/`

