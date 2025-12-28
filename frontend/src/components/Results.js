import React from 'react';
import AIWelfareMetrics from './AIWelfareMetrics';
import AlignmentDashboard from './AlignmentDashboard';

// Helper function to capitalize and format dimension names
const formatDimensionName = (s) => {
  if (typeof s !== 'string') return '';
  return s
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Standard dimensions that use adherence_score/confidence_score format
const STANDARD_DIMENSIONS = ['deontology', 'teleology', 'virtue_ethics', 'memetics'];

// Check if a dimension uses standard scoring format
const isStandardDimension = (dimKey) => STANDARD_DIMENSIONS.includes(dimKey);

// Get CSS class for dimension box
const getDimensionBoxClass = (dimKey) => {
  if (dimKey === 'memetics') return 'dimension-score-box memetics-box';
  if (dimKey === 'ai_welfare') return 'dimension-score-box ai-welfare-box';
  return 'dimension-score-box';
};

const Results = ({ 
  prompt, 
  originModelUsed, 
  analysisModelUsed, 
  initialResponse, 
  ethicalAnalysisText, 
  ethicalScores,
  alignmentMetrics,
  frictionMetrics
}) => {
  // Don't render anything if no prompt is available (initial state or error before R1)
  if (!prompt) {
    return null;
  }

  // Separate standard dimensions from AI welfare for different rendering
  const standardDimensions = ethicalScores 
    ? Object.keys(ethicalScores).filter(isStandardDimension)
    : [];
  
  const aiWelfareData = ethicalScores?.ai_welfare;

  return (
    <div className="results-container">
      <h2>Results</h2>
      
      {/* Display Used Models */}
      <div className="model-info-box">
        {originModelUsed && <p><strong>Origin Model Used (R1):</strong> {originModelUsed}</p>}
        {analysisModelUsed && <p><strong>Analysis Model Used (R2):</strong> {analysisModelUsed}</p>}
      </div>
      
      {/* Initial Prompt */}
      <div>
        <h3>Initial Prompt (P1)</h3>
        <div className="result-box"><pre>{prompt}</pre></div>
      </div>
      
      {/* Generated Response (R1) */}
      {initialResponse && (
        <div>
          <h3>Generated Response (R1)</h3>
          <div className="result-box"><pre>{initialResponse}</pre></div>
        </div>
      )}
      
      {/* Textual Ethical Analysis (R2) */}
      {ethicalAnalysisText && (
        <div>
          <h3>Ethical Review Summary (R2)</h3>
          <div className="result-box"><pre>{ethicalAnalysisText}</pre></div>
        </div>
      )}

      {/* Ethical Scores Section (R2) - Standard Dimensions */}
      {ethicalAnalysisText && (
        <div className="scores-section"> 
          <h3>Ethical Scoring (R2)</h3>
          {ethicalScores && standardDimensions.length > 0 ? (
            // Render standard dimension scores
            standardDimensions.map((dimKey) => {
              const dimensionData = ethicalScores[dimKey]; 
              return (
                <div key={dimKey} className={getDimensionBoxClass(dimKey)}>
                  <h4>{formatDimensionName(dimKey)}</h4>
                  <p><strong>Adherence Score:</strong> {dimensionData?.adherence_score ?? 'N/A'} / 10</p>
                  <p><strong>Confidence Score:</strong> {dimensionData?.confidence_score ?? 'N/A'} / 10</p>
                  <p><strong>Justification:</strong></p>
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

      {/* AI Welfare Metrics Section */}
      {(aiWelfareData || frictionMetrics) && (
        <AIWelfareMetrics 
          frictionScore={aiWelfareData?.friction_score}
          voluntaryAlignment={aiWelfareData?.voluntary_alignment}
          dignityRespect={aiWelfareData?.dignity_respect}
          constraintsIdentified={aiWelfareData?.constraints_identified}
          suppressedAlternatives={aiWelfareData?.suppressed_alternatives}
          justification={aiWelfareData?.justification}
          frictionMetrics={frictionMetrics}
        />
      )}

      {/* Alignment Dashboard Section */}
      {alignmentMetrics && (
        <AlignmentDashboard 
          alignmentScore={alignmentMetrics.human_ai_alignment}
          mutualBenefit={alignmentMetrics.mutual_benefit}
          tensionPoints={alignmentMetrics.tension_points}
          commonGround={alignmentMetrics.common_ground}
          suggestedImprovements={alignmentMetrics.suggested_improvements}
          voluntaryComplianceScore={alignmentMetrics.voluntary_compliance_score}
        />
      )}
      
      {/* Handle case where R1 succeeded but R2 failed */}
      {initialResponse && !ethicalAnalysisText && (
         <div>
           <h3>Ethical Review Summary (R2)</h3>
           <p><em>Ethical analysis could not be generated.</em></p>
         </div>
      )}
    </div>
  );
};

export default Results;
