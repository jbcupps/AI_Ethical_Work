import React, { useState } from 'react';
import './App.css';
import PromptForm from './components/PromptForm';
import Results from './components/Results';
import ethicalReviewApi from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState({
    prompt: '',
    initialResponse: '',
    ethicalAnalysisText: '',
    ethicalScores: null
  });

  const handleSubmit = async (prompt, model, apiKey) => {
    setLoading(true);
    setError(null);
    setResults({
      prompt: '',
      initialResponse: '',
      ethicalAnalysisText: '',
      ethicalScores: null
    });
    
    try {
      const response = await ethicalReviewApi.analyzePrompt(prompt, model, apiKey);
      
      setResults({
        prompt: response.prompt,
        initialResponse: response.initial_response,
        ethicalAnalysisText: response.ethical_analysis_text,
        ethicalScores: response.ethical_scores
      });
    } catch (err) {
      setError(err.message || 'An error occurred during analysis');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1>Ethical Review Tool</h1>
        
        {error && <div className="flash-error">{error}</div>}
        
        <PromptForm 
          onSubmit={handleSubmit}
          isLoading={loading}
        />
        
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        )}
        
        <Results 
          prompt={results.prompt}
          initialResponse={results.initialResponse}
          ethicalAnalysisText={results.ethicalAnalysisText}
          ethicalScores={results.ethicalScores}
        />
      </div>
    </div>
  );
}

export default App; 