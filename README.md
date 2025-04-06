# Ethical Review Tool

A web application for generating and ethically analyzing AI responses across various LLM models.

## Architecture

This application is built with a modern two-tier architecture:

1. **Backend API**: A Flask-based RESTful API that handles:
   - Interacting with AI models (Gemini and Anthropic)
   - Ethical analysis using a defined ontology
   - Model selection and configuration
   
2. **Frontend Web UI**: A React-based single-page application that provides:
   - User interface for entering prompts
   - Selection of AI models
   - Display of results and analysis

## Directory Structure

```
ethical-review-tool/
├── backend/                # Backend API service
│   ├── app/                # Flask app
│   │   ├── modules/        # Modules for LLM interaction
│   │   ├── __init__.py     # Flask app factory
│   │   ├── api.py          # API routes
│   │   └── ontology.md     # Ethical framework file
│   ├── wsgi.py             # WSGI entry point
│   ├── Dockerfile          # Backend container definition
│   └── requirements.txt    # Python dependencies
├── frontend/               # Frontend web app
│   ├── src/                # React source code
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── App.js          # Main App component
│   │   └── index.js        # Entry point
│   ├── public/             # Static assets
│   ├── Dockerfile          # Frontend container definition
│   ├── nginx.conf          # Nginx configuration
│   └── package.json        # Node.js dependencies
├── context/                # Logs directory
├── .env                    # Environment variables
└── docker-compose.yml      # Docker services definition
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- API Keys for:
  - Google Gemini
  - Anthropic Claude (optional)

### Environment Setup

Create a `.env` file in the root directory with your API keys:

```
# API Keys
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional API endpoints (for custom/proxy endpoints)
# GEMINI_API_ENDPOINT=your_custom_endpoint
# ANTHROPIC_API_ENDPOINT=your_custom_endpoint
```

### Running with Docker Compose

1. Build and start the containers:

```bash
docker-compose up -d
```

2. Access the application:
   - Frontend: http://localhost:80
   - Backend API: http://localhost:5000/api

### API Endpoints

The backend provides the following API endpoints:

- `GET /api/models`: Returns a list of available LLM models
- `POST /api/analyze`: Analyzes a prompt using the specified model
  ```json
  {
    "prompt": "The text to analyze",
    "model": "gemini-1.5-flash-latest",
    "api_key": "optional_api_key_override"
  }
  ```

## Development

### Backend Development

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Run the development server:
```bash
cd backend
python wsgi.py
```

### Frontend Development

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## License

[Your license information here]

## Acknowledgments

- Google Gemini API
- Anthropic Claude API 