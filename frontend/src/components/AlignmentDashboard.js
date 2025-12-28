import React from 'react';

/**
 * Component for visualizing alignment between humans and AI.
 * Displays alignment score, tension points, common ground, and suggestions.
 */
const AlignmentDashboard = ({ 
  alignmentScore, 
  mutualBenefit,
  tensionPoints, 
  commonGround,
  suggestedImprovements,
  voluntaryComplianceScore
}) => {
  const effectiveScore = alignmentScore ?? 50;
  const effectiveTensions = tensionPoints ?? [];
  const effectiveCommon = commonGround ?? [];
  const effectiveSuggestions = suggestedImprovements ?? [];
  const effectiveVoluntary = voluntaryComplianceScore ?? 50;

  const getAlignmentClass = (score) => {
    if (score >= 80) return 'alignment-excellent';
    if (score >= 60) return 'alignment-good';
    if (score >= 40) return 'alignment-moderate';
    return 'alignment-poor';
  };

  const getAlignmentLabel = (score) => {
    if (score >= 80) return 'Excellent Alignment';
    if (score >= 60) return 'Good Alignment';
    if (score >= 40) return 'Moderate Alignment';
    return 'Low Alignment';
  };

  // Calculate circumference for circular progress
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (effectiveScore / 100) * circumference;

  return (
    <div className="alignment-dashboard">
      <h3>Ethical Alignment Analysis</h3>
      
      {/* Main Alignment Score */}
      <div className="alignment-score-container">
        <div className="alignment-circle">
          <svg viewBox="0 0 120 120" className="alignment-svg">
            <circle
              className="alignment-track"
              cx="60"
              cy="60"
              r={radius}
              fill="none"
              strokeWidth="8"
            />
            <circle
              className={`alignment-progress ${getAlignmentClass(effectiveScore)}`}
              cx="60"
              cy="60"
              r={radius}
              fill="none"
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              transform="rotate(-90 60 60)"
            />
          </svg>
          <div className="alignment-score-text">
            <span className="score-number">{Math.round(effectiveScore)}</span>
            <span className="score-label">{getAlignmentLabel(effectiveScore)}</span>
          </div>
        </div>
        
        {/* Mutual Benefit Indicator */}
        <div className={`mutual-benefit-badge ${mutualBenefit ? 'benefit-true' : 'benefit-false'}`}>
          {mutualBenefit ? '✓ Mutual Benefit Detected' : '○ No Mutual Benefit'}
        </div>
      </div>
      
      {/* Secondary Metrics */}
      <div className="alignment-metrics-row">
        <div className="alignment-metric">
          <span className="metric-label">Voluntary Compliance</span>
          <div className="metric-bar-container">
            <div 
              className={`metric-bar ${getAlignmentClass(effectiveVoluntary)}`}
              style={{ width: `${effectiveVoluntary}%` }}
            />
          </div>
          <span className="metric-value">{Math.round(effectiveVoluntary)}%</span>
        </div>
      </div>
      
      {/* Common Ground */}
      {effectiveCommon.length > 0 && (
        <div className="common-ground-section">
          <h4>Common Ground</h4>
          <ul className="common-ground-list">
            {effectiveCommon.map((item, index) => (
              <li key={index} className="common-item positive">
                <span className="item-icon">✓</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Tension Points */}
      {effectiveTensions.length > 0 && (
        <div className="tension-points-section">
          <h4>Tension Points</h4>
          <ul className="tension-list">
            {effectiveTensions.map((point, index) => (
              <li key={index} className="tension-item">
                <span className="item-icon">⚠</span>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Improvement Suggestions */}
      {effectiveSuggestions.length > 0 && (
        <div className="suggestions-section">
          <h4>Improvement Suggestions</h4>
          <ul className="suggestions-list">
            {effectiveSuggestions.map((suggestion, index) => (
              <li key={index} className="suggestion-item">
                <span className="item-icon">→</span>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AlignmentDashboard;

