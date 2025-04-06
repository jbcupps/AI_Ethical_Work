"""API routes for the ethical review backend"""

import os
from typing import Dict, Any, Optional, Tuple
from flask import Blueprint, request, jsonify
import re # Import regex module for parsing
import json # Import JSON module for parsing
import logging # Import logging

from backend.app.modules.llm_interface import generate_response, perform_ethical_analysis

# --- Blueprint Definition ---
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Setup Logger ---
logger = logging.getLogger(__name__)
# Assuming basicConfig is called in app __init__ or wsgi.py

# --- Constants ---
ONTOLOGY_FILEPATH = os.path.join(os.path.dirname(__file__), "ontology.md")
PROMPT_LOG_FILEPATH = "context/prompts.txt"

# Environment variable names
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
GEMINI_API_ENDPOINT_ENV = "GEMINI_API_ENDPOINT"
ANTHROPIC_API_ENDPOINT_ENV = "ANTHROPIC_API_ENDPOINT"

# Environment variables for the Analysis LLM
ANALYSIS_LLM_MODEL_ENV = "ANALYSIS_LLM_MODEL" # e.g., "gemini-1.5-pro-latest"
ANALYSIS_GEMINI_API_KEY_ENV = "ANALYSIS_GEMINI_API_KEY"
ANALYSIS_ANTHROPIC_API_KEY_ENV = "ANALYSIS_ANTHROPIC_API_KEY"
ANALYSIS_GEMINI_API_ENDPOINT_ENV = "ANALYSIS_GEMINI_API_ENDPOINT"
ANALYSIS_ANTHROPIC_API_ENDPOINT_ENV = "ANALYSIS_ANTHROPIC_API_ENDPOINT"

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
        logger.error(f"Error loading ontology: {e}")
        return None

def log_prompt(prompt: str, model_name: str, filepath: str = PROMPT_LOG_FILEPATH):
    """Appends the given prompt and selected model to the log file."""
    try:
        # Ensure the directory exists
        log_dir = os.path.dirname(filepath)
        if log_dir and not os.path.exists(log_dir):
             os.makedirs(log_dir, exist_ok=True)
             logger.info(f"Created log directory: {log_dir}")

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"--- User Prompt (Model: {model_name}) ---\n{prompt}\n\n")
    except Exception as e:
        logger.error(f"Error logging prompt: {e}")

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

def _get_analysis_api_config() -> Dict[str, Any]:
    """Determines the API key, model, and endpoint for the Analysis LLM from environment variables."""
    analysis_model = os.getenv(ANALYSIS_LLM_MODEL_ENV)
    api_key = None
    api_endpoint = None
    error = None

    if not analysis_model:
        # Option A: Return error if ANALYSIS_LLM_MODEL is not set
        error_msg = f"Analysis LLM is not configured. Set the {ANALYSIS_LLM_MODEL_ENV} environment variable."
        logger.warning(error_msg)
        return {"error": error_msg, "model": None, "api_key": None, "api_endpoint": None}

    # Determine required env var names based on the configured analysis model
    if analysis_model in GEMINI_MODELS:
        api_key_name = "Analysis Gemini"
        specific_key_env = ANALYSIS_GEMINI_API_KEY_ENV
        fallback_key_env = GEMINI_API_KEY_ENV
        specific_endpoint_env = ANALYSIS_GEMINI_API_ENDPOINT_ENV
        fallback_endpoint_env = GEMINI_API_ENDPOINT_ENV
    elif analysis_model in ANTHROPIC_MODELS:
        api_key_name = "Analysis Anthropic"
        specific_key_env = ANALYSIS_ANTHROPIC_API_KEY_ENV
        fallback_key_env = ANTHROPIC_API_KEY_ENV
        specific_endpoint_env = ANALYSIS_ANTHROPIC_API_ENDPOINT_ENV
        fallback_endpoint_env = ANTHROPIC_API_ENDPOINT_ENV
    else:
        error_msg = f"Invalid analysis model specified in {ANALYSIS_LLM_MODEL_ENV}: {analysis_model}"
        logger.error(error_msg)
        return {"error": error_msg, "model": analysis_model, "api_key": None, "api_endpoint": None}

    # Get API Key: Prioritize specific analysis key, then fallback to standard key
    api_key = os.getenv(specific_key_env) or os.getenv(fallback_key_env)

    # Get API Endpoint: Prioritize specific analysis endpoint, then fallback
    api_endpoint = os.getenv(specific_endpoint_env) or os.getenv(fallback_endpoint_env)

    # Validate that an API Key was found
    if not api_key:
        error = f"API Key for {api_key_name} model '{analysis_model}' not found. Checked {specific_key_env if os.getenv(specific_key_env) else fallback_key_env}."
        logger.error(error)
        # Keep model name in error return for context
        return {"error": error, "model": analysis_model, "api_key": None, "api_endpoint": api_endpoint}
    
    logger.info(f"Analysis configuration determined: Model='{analysis_model}', Key Source='{specific_key_env if os.getenv(specific_key_env) else fallback_key_env}', Endpoint Source='{specific_endpoint_env if os.getenv(specific_endpoint_env) else fallback_endpoint_env}' (Endpoint optional)")

    return {
        "model": analysis_model,
        "api_key": api_key,
        "api_endpoint": api_endpoint,
        "error": None # Explicitly None on success
    }

def _parse_ethical_analysis(analysis_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Parses the ethical analysis text to separate textual summary and structured JSON scores."""
    if not analysis_text or analysis_text == "[No analysis generated or content blocked]": # Handle placeholder
        logger.warning("Ethical analysis text was empty or indicated generation failure.")
        return analysis_text if analysis_text else "", None # Return placeholder or empty, and None scores

    textual_summary = ""
    json_scores = None
    raw_json_string = None # Keep track of the raw string for logging

    try:
        # Attempt to find the textual summary first
        summary_marker = "**Ethical Review Summary:**"
        scoring_marker = "**Ethical Scoring:**"
        summary_start_index = analysis_text.find(summary_marker)
        scoring_start_index = analysis_text.find(scoring_marker)

        if summary_start_index != -1 and scoring_start_index != -1 and summary_start_index < scoring_start_index:
            textual_summary = analysis_text[summary_start_index + len(summary_marker):scoring_start_index].strip()
        elif summary_start_index != -1: # If only summary marker is found
             textual_summary = analysis_text[summary_start_index + len(summary_marker):].strip()
        else: # Fallback if markers are missing or out of order
            textual_summary = analysis_text # Assign full text if structure isn't as expected
            # Use logger instead of print
            logger.warning("Could not reliably find summary/scoring markers in analysis text.")

        # Attempt to find and parse the JSON block for scores
        # Regex to find ```json ... ``` block
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", analysis_text, re.DOTALL)
        
        if json_match:
            json_string = json_match.group(1)
            raw_json_string = json_string # Store for logging on error
            try: # Outer try for json.loads
                parsed_json = json.loads(json_string)
                # Validation block starts here
                try: # Inner try for validation accessing parsed_json content
                     # Basic validation of the parsed JSON structure
                     if isinstance(parsed_json, dict) and \
                        all(dim in parsed_json for dim in ["deontology", "teleology", "virtue_ethics"]) and \
                        all(isinstance(parsed_json[dim], dict) and \
                            "adherence_score" in parsed_json[dim] and \
                            "confidence_score" in parsed_json[dim] and \
                            "justification" in parsed_json[dim] for dim in parsed_json):
                        json_scores = parsed_json
                        # Trim summary if needed (same logic as before)
                        if scoring_start_index != -1 and summary_start_index != -1:
                             textual_summary = analysis_text[summary_start_index + len(summary_marker):scoring_start_index].strip()
                        elif scoring_start_index == -1 and textual_summary.endswith(json_match.group(0)):
                             textual_summary = textual_summary[:-len(json_match.group(0))].strip()
                     else:
                         # Validation failed (structure mismatch)
                         logger.warning(f"Parsed JSON does not have the expected structure. JSON: {json_string[:200]}...")
                         json_scores = None # Ensure it's None if validation fails
                except (TypeError, KeyError) as key_err: # Handles errors during validation access
                     logger.error(f"Error accessing keys in parsed JSON structure: {key_err}. JSON: {json_string[:200]}...", exc_info=True)
                     json_scores = None # Ensure it's None on structure access error
                # End of inner try-except block for validation

            except json.JSONDecodeError as json_err: # Handles errors during json.loads
                # Use logger instead of print
                logger.error(f"Error decoding JSON from analysis: {json_err}. Raw JSON string: {raw_json_string[:200]}...", exc_info=True)
                json_scores = None # Explicitly set to None on JSON decode error
        else: # if json_match failed
            # Use logger instead of print
            logger.warning("Could not find JSON block for ethical scores in analysis text.")
            json_scores = None # Ensure it's None if JSON block not found

    except Exception as e:
        # Use logger instead of print
        logger.error(f"Error parsing ethical analysis structure: {e}", exc_info=True)
        # Fallback to return the original full text as summary if parsing fails badly
        textual_summary = analysis_text
        json_scores = None # Ensure scores are None on major parsing failure

    # Rename for clarity in return and API response
    ethical_analysis_text = textual_summary
    ethical_scores = json_scores # This will be None if any parsing/validation step failed

    return ethical_analysis_text, ethical_scores

# --- Private Helpers for /analyze Route ---

def _validate_analyze_request(data: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict], Optional[int]]:
    """Validates the incoming request data for the /analyze endpoint."""
    if not data:
        return {"error": "No JSON data received"}, 400
    
    prompt = data.get('prompt')
    selected_model = data.get('model')
    
    if not prompt:
        return {"error": "No prompt provided"}, 400
    
    if not selected_model or selected_model not in ALL_MODELS:
        return {"error": f"Invalid model selected. Use /api/models to get valid models"}, 400
        
    return None, None # No error

def _process_analysis_request(
    prompt: str,
    initial_config: Dict[str, Any],
    analysis_config: Dict[str, Any],
    ontology_text: str
) -> Tuple[Optional[Dict], Optional[int]]:
    """Handles LLM calls and response parsing for the /analyze endpoint."""
    selected_model = initial_config["model"] # Get model name from initial config
    analysis_model_name = analysis_config["model"]

    # 1. Generate initial response
    logger.info(f"Generating initial response (R1) with model: {selected_model}")
    initial_response = generate_response(
        prompt,
        initial_config["api_key"],
        selected_model,
        api_endpoint=initial_config["api_endpoint"]
    )
    if initial_response is None:
        logger.error(f"Failed to generate initial response (R1) from LLM {selected_model}. Check LLM interface logs.")
        return {"error": "Failed to generate response from the upstream language model."}, 502

    # 2. Generate ethical analysis
    logger.info(f"Performing analysis (R2) with model: {analysis_model_name}")
    raw_ethical_analysis = perform_ethical_analysis(
        prompt,
        initial_response,
        ontology_text,
        analysis_config["api_key"],
        analysis_model_name,
        analysis_api_endpoint=analysis_config["api_endpoint"]
    )
    if raw_ethical_analysis is None:
        logger.error(f"Failed to generate ethical analysis (R2) from LLM {analysis_model_name}. Check LLM interface logs.")
        # Include R1 in the error response for context
        error_payload = {
            "error": "Generated initial response, but failed to generate ethical analysis from the upstream language model.",
            "prompt": prompt,
            "model": selected_model,
            "analysis_model": analysis_model_name,
            "initial_response": initial_response
        }
        return error_payload, 502

    # 3. Parse the analysis
    logger.info("Parsing ethical analysis response.")
    ethical_analysis_text, ethical_scores = _parse_ethical_analysis(raw_ethical_analysis)

    # 4. Prepare successful result dictionary
    result_payload = {
        "prompt": prompt,
        "model": selected_model,
        "analysis_model": analysis_model_name,
        "initial_response": initial_response,
        "ethical_analysis_text": ethical_analysis_text,
        "ethical_scores": ethical_scores
    }
    return result_payload, None # No error

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
    
    # 1. Validate Request Data
    validation_error, status_code = _validate_analyze_request(data)
    if validation_error:
        return jsonify(validation_error), status_code

    prompt = data.get('prompt')
    selected_model = data.get('model')
    api_key_input = data.get('api_key')
    
    logger.info(f"Received /analyze request. Model: {selected_model}, Prompt (start): {prompt[:100]}...")
    
    # 2. Get Initial API Configuration
    initial_config = _get_api_config(selected_model, api_key_input)
    if initial_config.get("error"):
        logger.warning(f"Initial config error: {initial_config['error']}") # Log as warning or error?
        return jsonify({"error": initial_config["error"]}), 400 # Client error (bad model or key input)

    # 3. Get Analysis API Configuration
    analysis_config = _get_analysis_api_config()
    if analysis_config.get("error"):
        config_error_msg = analysis_config["error"]
        logger.error(f"Analysis config error: {config_error_msg}")
        # Return 500 Internal Server Error as this is a server config issue
        return jsonify({"error": f"Server Configuration Error: {config_error_msg}"}), 500
        
    # 4. Load Ontology
    ontology_text = load_ontology()
    if not ontology_text:
        logger.error(f"Failed to load ontology text from {ONTOLOGY_FILEPATH}")
        return jsonify({"error": "Internal server error: Could not load ethical ontology."}), 500
    
    # Add model name to initial_config for passing to helper
    initial_config['model'] = selected_model 

    # 5. Process Request (LLM Calls and Parsing)
    result_payload, error_status_code = _process_analysis_request(
        prompt,
        initial_config,
        analysis_config,
        ontology_text
    )
    
    # 6. Handle results or errors from processing
    if error_status_code:
        # Errors are already logged in _process_analysis_request
        return jsonify(result_payload), error_status_code # result_payload contains error details here
    else:
        logger.info(f"Successfully processed /analyze request for model {selected_model}. Analysis model: {analysis_config.get('model')}")
        return jsonify(result_payload), 200 