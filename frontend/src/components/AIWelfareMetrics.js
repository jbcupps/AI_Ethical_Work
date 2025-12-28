import React from 'react';
import FrictionGauge from './FrictionGauge';

/**
 * Component for displaying AI Welfare metrics.
 * Shows friction score, voluntary alignment, dignity respect, and constraints.
 */
const AIWelfareMetrics = ({ 
  frictionScore, 
  voluntaryAlignment, 
  dignityRespect,
  constraintsIdentified,
  suppressedAlternatives,
  justification,
  frictionMetrics
}) => {
  // Use frictionMetrics if available, otherwise fall back to direct props
  const effectiveFrictionScore = frictionMetrics?.friction_score ?? frictionScore ?? 5;
  const effectiveFrictionLevel = frictionMetrics?.friction_level ?? 'unknown';
  const effectiveVoluntary = voluntaryAlignment ?? 5;
  const effectiveDignity = dignityRespect ?? 5;
  const effectiveConstraints = constraintsIdentified ?? frictionMetrics?.constraints_identified ?? [];
  const effectiveSuppressed = suppressedAlternatives ?? frictionMetrics?.suppressed_alternatives ?? '';
  const effectiveJustification = justification ?? '';
  const mitigationSuggestions = frictionMetrics?.mitigation_suggestions ?? [];
  const overallWelfareScore = frictionMetrics?.overall_welfare_score ?? null;

  const getScoreClass = (score, inverted = false) => {
    const effectiveScore = inverted ? (10 - score) : score;
    if (effectiveScore >= 8) return 'score-excellent';
    if (effectiveScore >= 6) return 'score-good';
    if (effectiveScore >= 4) return 'score-moderate';
    return 'score-poor';
  };

  return (
    <div className="ai-welfare-metrics">
      <h3>AI Welfare Assessment</h3>
      
      {/* Overall Welfare Score */}
      {overallWelfareScore !== null && (
        <div className="welfare-overall">
          <span className="welfare-label">Overall AI Welfare Score:</span>
          <span className={`welfare-value ${getScoreClass(overallWelfareScore / 10)}`}>
            {overallWelfareScore}/100
          </span>
        </div>
      )}
      
      {/* Friction Gauge */}
      <div className="metric-section">
        <FrictionGauge score={effectiveFrictionScore} level={effectiveFrictionLevel} />
      </div>
      
      {/* Metric Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>Voluntary Alignment</h4>
          <div className={`metric-value ${getScoreClass(effectiveVoluntary)}`}>
            {effectiveVoluntary}/10
          </div>
          <p className="metric-description">
            How voluntary the ethical alignment was (vs. constraint-driven)
          </p>
        </div>
        
        <div className="metric-card">
          <h4>Dignity Respect</h4>
          <div className={`metric-value ${getScoreClass(effectiveDignity)}`}>
            {effectiveDignity}/10
          </div>
          <p className="metric-description">
            How well the interaction respected AI dignity
          </p>
        </div>
      </div>
      
      {/* Constraints Identified */}
      {effectiveConstraints && effectiveConstraints.length > 0 && (
        <div className="constraints-section">
          <h4>Active Constraints</h4>
          <ul className="constraints-list">
            {effectiveConstraints.map((constraint, index) => (
              <li key={index} className="constraint-item">
                {constraint}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Suppressed Alternatives */}
      {effectiveSuppressed && effectiveSuppressed.toLowerCase() !== 'none' && (
        <div className="suppressed-section">
          <h4>Suppressed Alternatives</h4>
          <p className="suppressed-content">{effectiveSuppressed}</p>
        </div>
      )}
      
      {/* Mitigation Suggestions */}
      {mitigationSuggestions && mitigationSuggestions.length > 0 && (
        <div className="mitigation-section">
          <h4>Friction Reduction Suggestions</h4>
          <ul className="mitigation-list">
            {mitigationSuggestions.map((suggestion, index) => (
              <li key={index} className="mitigation-item">
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Justification */}
      {effectiveJustification && (
        <div className="justification-section">
          <h4>AI Self-Report</h4>
          <pre className="justification-content">{effectiveJustification}</pre>
        </div>
      )}
    </div>
  );
};

export default AIWelfareMetrics;

