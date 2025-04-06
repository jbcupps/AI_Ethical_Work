import axios from 'axios';

// Set the base URL for the API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create an axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API services
export const ethicalReviewApi = {
  // Get list of available models
  getModels: async () => {
    try {
      const response = await apiClient.get('/models');
      return response.data.models;
    } catch (error) {
      console.error('Error fetching models:', error);
      throw error;
    }
  },
  
  // Submit a prompt for analysis
  analyzePrompt: async (prompt, model, apiKey = null) => {
    try {
      const payload = {
        prompt,
        model,
        api_key: apiKey,
      };
      
      const response = await apiClient.post('/analyze', payload);
      return response.data;
    } catch (error) {
      console.error('Error analyzing prompt:', error);
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  }
};

export default ethicalReviewApi; 