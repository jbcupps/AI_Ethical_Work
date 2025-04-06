import React, { useState, useEffect } from 'react';
import ethicalReviewApi from '../services/api';

const PromptForm = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [models, setModels] = useState([]);
  const [error, setError] = useState('');
  
  // Fetch available models on component mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const modelList = await ethicalReviewApi.getModels();
        setModels(modelList);
        // Set default model
        if (modelList.length > 0) {
          setSelectedModel(modelList[0]);
        }
      } catch (err) {
        setError('Error loading models. Please try again later.');
        console.error('Error fetching models:', err);
      }
    };
    
    fetchModels();
  }, []);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a prompt.');
      return;
    }
    
    setError('');
    onSubmit(prompt, selectedModel, apiKey || null);
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
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="model-select">Select Model:</label>
          <select
            id="model-select"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={isLoading || models.length === 0}
          >
            {models.map(model => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="api-key">
            API Key (Optional - uses environment variable if blank):
          </label>
          <input
            type="password"
            id="api-key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            disabled={isLoading}
          />
        </div>
        
        <button type="submit" disabled={isLoading || !selectedModel}>
          {isLoading ? 'Processing...' : 'Generate & Analyze'}
        </button>
      </form>
    </div>
  );
};

export default PromptForm; 