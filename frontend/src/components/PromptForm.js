import React, { useState } from 'react';

const PromptForm = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a prompt.');
      return;
    }
    
    setError('');
    // Pass null for model and apiKey to use server defaults
    onSubmit(prompt, null, null);
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
            placeholder="Enter your prompt here. The system will use the default API keys and model configuration."
          />
        </div>
        
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Generate & Analyze'}
        </button>
      </form>
    </div>
  );
};

export default PromptForm; 