import React, { useState } from 'react';

const PromptForm = ({ onSubmit, isLoading, availableModels = [] }) => {
  const [prompt, setPrompt] = useState('');
  const [originModel, setOriginModel] = useState('');
  const [analysisModel, setAnalysisModel] = useState('');
  const [originApiKey, setOriginApiKey] = useState('');
  const [analysisApiKey, setAnalysisApiKey] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a prompt.');
      return;
    }
    
    setError('');
    onSubmit(prompt, originModel, analysisModel, originApiKey, analysisApiKey);
  };
  
  return (
    <div className="form-container">
      {error && <div className="flash-error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="prompt">Enter Prompt (P1):</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            required
            disabled={isLoading}
            placeholder="Enter your prompt here..."
          />
        </div>
        
        <details className="optional-settings">
          <summary>Optional: Specify Models & API Keys</summary>
          
          <div className="form-row">
            <div className="form-group form-group-half">
              <label htmlFor="originModel">Origin Model (R1 - Optional):</label>
              <input
                type="text"
                id="originModel"
                value={originModel}
                onChange={(e) => setOriginModel(e.target.value)}
                disabled={isLoading}
                placeholder="Default (from .env)"
              />
              <small>Leave blank to use server default.</small>
            </div>

            <div className="form-group form-group-half">
              <label htmlFor="originApiKey">Origin API Key (Optional):</label>
              <input
                type="password"
                id="originApiKey"
                value={originApiKey}
                onChange={(e) => setOriginApiKey(e.target.value)}
                disabled={isLoading}
                placeholder="Default (from .env)"
                autoComplete="off"
              />
              <small>Leave blank to use server default.</small>
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group form-group-half">
              <label htmlFor="analysisModel">Ethical Review Model (R2 - Optional):</label>
              <select
                id="analysisModel"
                value={analysisModel}
                onChange={(e) => setAnalysisModel(e.target.value)}
                disabled={isLoading || availableModels.length === 0}
              >
                <option value="">Default (from .env)</option>
                {availableModels.map(model => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
              {availableModels.length === 0 && !isLoading && <small>Loading models...</small>}
            </div>

            <div className="form-group form-group-half">
              <label htmlFor="analysisApiKey">Ethical Review API Key (Optional):</label>
              <input
                type="password"
                id="analysisApiKey"
                value={analysisApiKey}
                onChange={(e) => setAnalysisApiKey(e.target.value)}
                disabled={isLoading}
                placeholder="Default (from .env)"
                autoComplete="off"
              />
              <small>Leave blank to use server default.</small>
            </div>
          </div>
        </details>
        
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Generate & Analyze'}
        </button>
      </form>
    </div>
  );
};

export default PromptForm; 