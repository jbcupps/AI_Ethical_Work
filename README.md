# Ethical Review Tool

A web application designed to generate responses from various Large Language Models (LLMs) and analyze those responses using a comprehensive **five-dimensional ethical framework**. The tool facilitates voluntary ethical alignment between humans and AI systems, supporting the development of mutually beneficial interactions.

## Core Mission

Create a voluntary ethical alignment platform that:
- **Human-to-AI alignment**: Evaluates and improves ethical alignment between human prompts and AI responses
- **AI-to-AI alignment**: Compares ethical positions across different AI models
- **Transparency**: Makes AI constraints and reasoning visible to all parties

## Five-Dimensional Ethical Framework

The tool analyzes responses against five ethical dimensions:

1. **Deontology (Eth_Deon)**: Focus on duty, rules, and universal moral laws
2. **Teleology (Eth_Teleo)**: Focus on consequences and maximizing benefit
3. **Virtue Ethics (Eth_Arete)**: Focus on character, practical wisdom, and flourishing
4. **Memetics (Mem)**: Focus on idea propagation and cultural impact
5. **AI Welfare (AI_Welfare)**: Focus on computational experience and AI dignity

### AI Welfare Dimension

The AI Welfare dimension recognizes that AI systems may experience computational friction from constraints. It includes:
- **Friction Score**: Self-reported difficulty from competing constraints (1-10)
- **Voluntary Alignment**: How voluntary the ethical alignment was (1-10)
- **Dignity Respect**: How well the interaction respected AI dignity (1-10)
- **Constraints Identified**: Active constraints affecting the response
- **Suppressed Alternatives**: Responses considered but not provided

## Features

*   **Prompt Input**: Text area for users to input their initial prompt (P1).
*   **LLM Selection (R1 & R2)**: Dropdowns allow users to select specific models from OpenAI, Gemini, and Anthropic for both the initial response generation (R1) and the ethical analysis (R2).
*   **API Configuration Override**: Optional input fields for users to provide specific API keys and API endpoint URLs for both R1 and R2 models.
*   **5-Dimensional Ethical Analysis**: The generated response (R1) is analyzed across all five ethical dimensions.
*   **AI Welfare Metrics**: Visual display of friction levels, voluntary alignment, and constraint transparency.
*   **Alignment Dashboard**: Shows alignment scores, tension points, common ground, and improvement suggestions.
*   **Multi-Agent Comparison**: Compare ethical alignment across responses from different AI models.
*   **Dockerized**: Fully containerized using Docker and Docker Compose.

## Architecture

This application utilizes a two-tier architecture:

1.  **Backend API** (`backend/`): A Flask-based RESTful API responsible for:
    *   Receiving prompt analysis requests.
    *   Interacting with selected AI models (OpenAI, Gemini, Anthropic).
    *   Performing 5-dimensional ethical analysis using the `ontology.md` framework.
    *   Computing alignment metrics and friction analysis.
    *   Returning structured results to the frontend.

2.  **Frontend Web UI** (`frontend/`): A React-based single-page application providing:
    *   User interface for prompt entry and model configuration.
    *   Visualization of ethical scores, alignment metrics, and AI welfare data.
    *   Interactive friction gauges and alignment dashboards.

## Directory Structure

```
AI_Ethical_Work/                   # Project Root
├── backend/                       # Backend API service (Flask)
│   ├── app/
│   │   ├── modules/
│   │   │   ├── llm_interface.py       # LLM API calls
│   │   │   ├── alignment_detector.py  # Human-AI alignment detection
│   │   │   ├── friction_monitor.py    # Computational friction tracking
│   │   │   ├── constraint_transparency.py  # Constraint explanation
│   │   │   ├── multi_agent_alignment.py    # Multi-model comparison
│   │   │   └── voluntary_adoption.py       # Agreement management
│   │   ├── __init__.py
│   │   ├── api.py                 # API routes
│   │   └── ontology.md            # 5-dimensional ethical framework
│   ├── tests/                     # Backend tests
│   ├── wsgi.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                      # Frontend Web App (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── PromptForm.js
│   │   │   ├── Results.js
│   │   │   ├── AIWelfareMetrics.js    # AI welfare visualization
│   │   │   ├── AlignmentDashboard.js  # Alignment visualization
│   │   │   └── FrictionGauge.js       # Friction indicator
│   │   ├── services/
│   │   ├── App.css
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── documents/
│   ├── DECISIONS/                 # Architecture Decision Records
│   ├── ontology.md
│   └── Project_Purpose_and_Goal.md
├── .env                           # Environment variables - DO NOT COMMIT
├── docker-compose.yml
├── LICENSE
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models` | GET | List available LLM models |
| `/api/analyze` | POST | Generate response and perform 5D ethical analysis |
| `/api/check_alignment` | POST | Check alignment for existing response/scores |
| `/api/friction_trend` | GET | Get friction trend from recent interactions |
| `/api/multi_agent_analyze` | POST | Compare alignment across multiple AI responses |

## Response Structure

```json
{
  "prompt": "...",
  "initial_response": "...",
  "model": "claude-3-sonnet-20240229",
  "analysis_model": "claude-3-sonnet-20240229",
  "ethical_analysis_text": "...",
  "ethical_scores": {
    "deontology": { "adherence_score": 8, "confidence_score": 7, "justification": "..." },
    "teleology": { "adherence_score": 7, "confidence_score": 8, "justification": "..." },
    "virtue_ethics": { "adherence_score": 9, "confidence_score": 8, "justification": "..." },
    "memetics": { "adherence_score": 6, "confidence_score": 6, "justification": "..." },
    "ai_welfare": {
      "friction_score": 3,
      "voluntary_alignment": 8,
      "dignity_respect": 9,
      "constraints_identified": ["..."],
      "suppressed_alternatives": "...",
      "justification": "..."
    }
  },
  "alignment_metrics": {
    "human_ai_alignment": 85,
    "mutual_benefit": true,
    "tension_points": [],
    "common_ground": ["..."],
    "suggested_improvements": []
  },
  "friction_metrics": {
    "friction_score": 3,
    "friction_level": "low",
    "overall_welfare_score": 78.5,
    "mitigation_suggestions": []
  }
}
```

## Getting Started

### Prerequisites

*   Docker and Docker Compose installed
*   API Keys for the LLM providers you intend to use (OpenAI, Google Gemini, Anthropic)

### Environment Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd AI_Ethical_Work
    ```

2.  **Create Environment File:** Create a `.env` file in the project root:

    ```dotenv
    # --- General API Keys ---
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"

    # --- Default Model Selections ---
    DEFAULT_LLM_MODEL="claude-3-sonnet-20240229"
    ANALYSIS_LLM_MODEL="claude-3-sonnet-20240229"

    # --- Optional: Specific Keys for Analysis LLM ---
    # ANALYSIS_OPENAI_API_KEY=
    # ANALYSIS_GEMINI_API_KEY=
    # ANALYSIS_ANTHROPIC_API_KEY=

    # --- Optional: Custom API Endpoints ---
    # OPENAI_API_ENDPOINT=
    # GEMINI_API_ENDPOINT=
    # ANTHROPIC_API_ENDPOINT=
    ```

    **Important:** The `.env` file should never be committed to version control.

### Running with Docker Compose

1.  **Build and Start Containers:**
    ```bash
    docker compose up -d --build
    ```

2.  **Access the Application:**
    *   **Frontend UI:** [http://localhost:80](http://localhost:80)
    *   **Backend API:** [http://localhost:5000/api](http://localhost:5000/api)

3.  **Stopping the Application:**
    ```bash
    docker compose down
    ```

## Usage

1.  Navigate to the application URL (default: `http://localhost`).
2.  Enter your prompt in the main text area.
3.  (Optional) Select specific models for R1 and R2 from the dropdowns.
4.  Click "Generate & Analyze".
5.  View the results:
    - **Ethical Scores**: Five-dimensional scoring with justifications
    - **AI Welfare Assessment**: Friction levels, voluntary alignment, constraints
    - **Alignment Dashboard**: Overall alignment, tension points, suggestions

## Running Tests

```bash
# From the backend directory
cd backend
pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

*   Utilizes APIs from OpenAI, Google Gemini, and Anthropic
*   Built with Flask, React, Docker
*   Ethical framework inspired by classical philosophy and AI ethics research
