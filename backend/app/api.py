"""API routes for the ethical review backend"""

import os
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify

from backend.app.modules.llm_interface import generate_response, perform_ethical_analysis

# --- Blueprint Definition ---
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Constants ---
ONTOLOGY_FILEPATH = os.path.join(os.path.dirname(__file__), "ontology.md")
PROMPT_LOG_FILEPATH = "context/prompts.txt"

# Environment variable names
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
GEMINI_API_ENDPOINT_ENV = "GEMINI_API_ENDPOINT"
ANTHROPIC_API_ENDPOINT_ENV = "ANTHROPIC_API_ENDPOINT"

# --- Model Definitions ---
GEMINI_MODELS = [
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash-latest",
    "gemini-1.0-pro",
]

ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]

ALL_MODELS = GEMINI_MODELS + ANTHROPIC_MODELS

# --- Helper Functions ---

def load_ontology(filepath: str = ONTOLOGY_FILEPATH) -> Optional[str]:
    """Loads the ethical ontology text from the specified file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading ontology: {e}")
        return None

def log_prompt(prompt: str, model_name: str, filepath: str = PROMPT_LOG_FILEPATH):
    """Appends the given prompt and selected model to the log file."""
    try:
        # Ensure the directory exists
        log_dir = os.path.dirname(filepath)
        if log_dir and not os.path.exists(log_dir):
             os.makedirs(log_dir, exist_ok=True)
             print(f"Created log directory: {log_dir}")

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"--- User Prompt (Model: {model_name}) ---\n{prompt}\n\n")
    except Exception as e:
        print(f"Error logging prompt: {e}")

def _get_api_config(selected_model: str, form_api_key: Optional[str]) -> Dict[str, Any]:
    """Determines the API key and endpoint based on model and form input."""
    api_key = None
    api_endpoint = None
    error = None
    
    # Determine required env var names based on model
    if selected_model in GEMINI_MODELS:
        api_key_name = "Gemini"
        env_var_key = GEMINI_API_KEY_ENV
        env_var_endpoint = GEMINI_API_ENDPOINT_ENV
    elif selected_model in ANTHROPIC_MODELS:
        api_key_name = "Anthropic"
        env_var_key = ANTHROPIC_API_KEY_ENV
        env_var_endpoint = ANTHROPIC_API_ENDPOINT_ENV
    else:
        return {"error": "Invalid model specified"}

    # Prioritize form input for the key
    if form_api_key:
        api_key = form_api_key
    else:
        # Fallback to environment variable for the key
        api_key = os.getenv(env_var_key)

    # Get endpoint from environment variable
    api_endpoint = os.getenv(env_var_endpoint)

    # Validate API Key
    if not api_key:
        error = f"API Key for {api_key_name} not provided via request or {env_var_key} env var."
    
    return {
        "api_key": api_key,
        "api_endpoint": api_endpoint,
        "error": error
    }

# --- API Routes ---

@api_bp.route('/models', methods=['GET'])
def get_models():
    """Return the list of available models"""
    return jsonify({
        "models": ALL_MODELS
    })

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    """Generate a response and ethical analysis for the given prompt"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data received"}), 400
    
    prompt = data.get('prompt')
    selected_model = data.get('model')
    api_key_input = data.get('api_key')
    
    # Validate inputs
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    if not selected_model or selected_model not in ALL_MODELS:
        return jsonify({"error": f"Invalid model selected. Use /api/models to get valid models"}), 400
    
    # Log the prompt
    log_prompt(prompt, selected_model)
    
    # Get API configuration
    config = _get_api_config(selected_model, api_key_input)
    
    if config.get("error"):
        return jsonify({"error": config["error"]}), 400
    
    # Load ontology
    ontology_text = load_ontology()
    if not ontology_text:
        return jsonify({"error": "Failed to load ontology text"}), 500
    
    try:
        # Generate initial response
        initial_response = generate_response(
            prompt, 
            config["api_key"], 
            selected_model, 
            api_endpoint=config["api_endpoint"]
        )
        
        if not initial_response:
            initial_response = "[No response generated or content blocked]"
        
        # Generate ethical analysis
        ethical_analysis = perform_ethical_analysis(
            prompt,
            initial_response,
            ontology_text,
            config["api_key"],
            selected_model,
            api_endpoint=config["api_endpoint"]
        )
        
        if not ethical_analysis:
            ethical_analysis = "[No analysis generated or content blocked]"
        
        # Return the results
        return jsonify({
            "prompt": prompt,
            "model": selected_model,
            "initial_response": initial_response,
            "ethical_analysis": ethical_analysis
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500 