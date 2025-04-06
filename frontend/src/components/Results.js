import React from 'react';

// Helper function to capitalize the first letter
const capitalize = (s) => {
  if (typeof s !== 'string') return ''
  return s.charAt(0).toUpperCase() + s.slice(1).replace('_', ' ') // Replace underscore for display
}

const Results = ({ prompt, initialResponse, ethicalAnalysisText, ethicalScores }) => {
  // Don't render anything if no prompt is available (initial state)
  if (!prompt) {
    return null;
  }

  const scoreDimensions = ethicalScores ? Object.keys(ethicalScores) : [];

  return (
    <div className="results-container">
      <h2>Results</h2>
      
      {/* Initial Prompt */}
      <div>
        <h3>Initial Prompt (P1)</h3>
        <div className="result-box"><pre>{prompt}</pre></div>
      </div>
      
      {/* Generated Response */}
      {initialResponse && (
        <div>
          <h3>Generated Response (R1)</h3>
          <div className="result-box"><pre>{initialResponse}</pre></div>
        </div>
      )}
      
      {/* Textual Ethical Analysis */}
      {ethicalAnalysisText && (
        <div>
          <h3>Ethical Review Summary</h3>
          <div className="result-box"><pre>{ethicalAnalysisText}</pre></div>
        </div>
      )}

      {/* Ethical Scores Section (Conditional) */}
      {ethicalAnalysisText && ( // Only show scoring section if analysis text exists
        <div className="scores-section"> 
          <h3>Ethical Scoring (R1)</h3>
          {ethicalScores && scoreDimensions.length > 0 ? (
            // Render scores if available
            scoreDimensions.map((dimKey) => {
              // Use optional chaining for safer access, though ?? handles missing values
              const dimensionData = ethicalScores?.[dimKey]; 
              return (
                <div key={dimKey} className="dimension-score-box">
                  <h4>{capitalize(dimKey)}</h4>
                  {/* Ensure dimensionData exists before accessing properties */}
                  <p><strong>Adherence Score:</strong> {dimensionData?.adherence_score ?? 'N/A'} / 10</p>
                  <p><strong>Confidence Score:</strong> {dimensionData?.confidence_score ?? 'N/A'} / 10</p>
                  <p><strong>Justification:</strong></p>
                  {/* Use optional chaining and fallback for justification */}
                  <pre>{dimensionData?.justification || 'N/A'}</pre>
                </div>
              );
            })
          ) : (
            // Render message if scores are missing but analysis text exists
            <p><em>Ethical scoring data could not be generated or parsed.</em></p>
          )}
        </div>
      )}
    </div>
  );
};

export default Results; 