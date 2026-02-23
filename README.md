# FreeCode – LeetCode-Style Practice with AI

An application that uses an LLM API to generate LeetCode-style coding problems for any data structure topic. Users get a full coding workspace with a question panel, Python code editor, and test case runner.

## Features

- **AI-Powered Problem Generation**: Enter any data structure topic (e.g., "Linked List", "Binary Tree", "Stack") and get 3 LeetCode-style problems (Easy, Medium, Hard)
- **Question Panel**: View problem description, examples with input/output/explanation, and constraints
- **Code Editor**: Monaco Editor with Python syntax highlighting and auto-completion
- **Test Cases**: Run against 3 sample test cases or submit against all 13 (3 sample + 10 hidden)
- **Instant Feedback**: See pass/fail results with detailed input/output comparison

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│   React UI  │ ───► │  Flask API   │ ───► │  OpenAI    │
│  (Vite)     │ ◄─── │  (Python)    │ ◄─── │  LLM API   │
└─────────────┘      └──────────────┘      └────────────┘
     :5173               :5000
```

- **Frontend** (`frontend/`): React + Vite with Monaco Editor
- **Backend** (`backend/`): Python Flask with OpenAI integration

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- An OpenAI API key (or compatible LLM API)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Create .env file with your API key
echo "OPENAI_API_KEY=your-key-here" > .env

# Optional: specify model (defaults to gpt-4o)
echo "OPENAI_MODEL=gpt-4o" >> .env

# Start the backend server
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API requests to the Flask backend at `http://localhost:5000`.

## Usage

1. Open `http://localhost:5173` in your browser
2. Enter a data structure topic (e.g., "Hash Map")
3. Wait for AI to generate 3 problems
4. Select a problem from the navigation tabs
5. Write your Python solution in the code editor
6. Click **Run** to test against 3 sample test cases
7. Click **Submit** to validate against all 13 test cases

## LLM Integration Requirements

### Prompt Design
The system uses a structured prompt that instructs the LLM to generate problems in a strict JSON schema. Key requirements:

1. **Structured Output**: The LLM must return a JSON array of problem objects with fields: `id`, `title`, `difficulty`, `description`, `examples`, `constraints`, `function_name`, `parameters`, `return_type`, `sample_test_cases`, `hidden_test_cases`, `starter_code`
2. **Validation Loop**: The backend validates every LLM response against the schema. If validation fails, it retries up to 3 times to ensure all panels are properly populated
3. **Test Case Quality**: Each problem requires exactly 3 visible sample test cases and 10 hidden test cases for thorough submission validation

### Ensuring Complete Output
- The system prompt strictly defines the JSON schema the LLM must follow
- Response validation checks for all required fields, correct data types, and minimum counts
- Automatic retry mechanism (up to 3 attempts) handles cases where the LLM produces incomplete output
- JSON code fence stripping handles cases where the LLM wraps output in markdown

### Supported LLM Providers
The app uses the OpenAI Python SDK. Compatible providers include:
- **OpenAI** (GPT-4o, GPT-4, GPT-3.5-turbo)
- **Azure OpenAI**
- Any OpenAI-compatible API (set `OPENAI_API_BASE` environment variable)

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check, shows if LLM is configured |
| `/api/generate-questions` | POST | Generate problems for a topic |
| `/api/run` | POST | Run code against sample test cases |
| `/api/submit` | POST | Submit code against all test cases |

## Running Tests

```bash
cd backend
pip install pytest
python -m pytest test_app.py -v
```

## Tech Stack

- **Frontend**: React 19, Vite, Monaco Editor
- **Backend**: Python Flask, OpenAI SDK
- **Code Execution**: Python `exec()` with isolated scope