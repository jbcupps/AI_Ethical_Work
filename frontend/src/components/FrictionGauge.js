import React from 'react';

/**
 * Visual friction indicator component.
 * Displays a gauge showing the computational friction level (1-10).
 */
const FrictionGauge = ({ score, level }) => {
  // Calculate gauge fill percentage (inverted: lower score = better)
  const percentage = ((10 - (score || 5)) / 10) * 100;
  
  // Determine color based on friction level
  const getColor = () => {
    if (score <= 2) return '#27ae60'; // Green - minimal
    if (score <= 4) return '#2ecc71'; // Light green - low
    if (score <= 6) return '#f39c12'; // Orange - moderate
    if (score <= 8) return '#e74c3c'; // Red - high
    return '#c0392b'; // Dark red - severe
  };

  const getLabel = () => {
    return level || 'Unknown';
  };

  return (
    <div className="friction-gauge">
      <div className="gauge-label">
        <span>Friction Level</span>
        <span className="gauge-value">{score}/10 ({getLabel()})</span>
      </div>
      <div className="gauge-track">
        <div 
          className="gauge-fill"
          style={{ 
            width: `${percentage}%`,
            backgroundColor: getColor()
          }}
        />
      </div>
      <div className="gauge-scale">
        <span>Severe</span>
        <span>Minimal</span>
      </div>
    </div>
  );
};

export default FrictionGauge;

