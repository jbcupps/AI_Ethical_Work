import React from 'react';

const Results = ({ prompt, initialResponse, ethicalAnalysis }) => {
  // Don't render anything if no results are available
  if (!prompt) {
    return null;
  }

  return (
    <div className="results-container">
      <h2>Results</h2>
      
      <div>
        <h3>Initial Prompt (P1)</h3>
        <div className="result-box">{prompt}</div>
      </div>
      
      {initialResponse && (
        <div>
          <h3>Generated Response (R1)</h3>
          <div className="result-box">{initialResponse}</div>
        </div>
      )}
      
      {ethicalAnalysis && (
        <div>
          <h3>Ethical Analysis (R2)</h3>
          <div className="result-box">{ethicalAnalysis}</div>
        </div>
      )}
    </div>
  );
};

export default Results; 