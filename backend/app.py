"""Flask backend for the LeetCode-style practice app."""

import ast
import json
import os
import traceback

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

from prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
    parse_llm_response,
)

load_dotenv()

app = Flask(__name__)
CORS(app)

MAX_RETRIES = 3


def get_llm_client() -> tuple[OpenAI | None, str | None, str | None]:
    """Create an LLM client based on the configured provider.

    Returns (client, model, error).
    Supports 'ollama' and 'openai' (default) providers via LLM_PROVIDER env var.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        # Ollama exposes an OpenAI-compatible API; use a placeholder API key.
        client = OpenAI(base_url=base_url, api_key="ollama")
        return client, model, None

    # Default: OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, None, "OPENAI_API_KEY not configured"
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return OpenAI(api_key=api_key), model, None


def call_llm(topic: str) -> tuple[list | None, str | None]:
    """Call the LLM to generate questions. Retries on validation failure."""
    client, model, error = get_llm_client()
    if error:
        return None, error

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(topic)},
                ],
                temperature=0.7,
                max_tokens=8000,
            )
            content = response.choices[0].message.content
            questions, errors = parse_llm_response(content)

            if not errors:
                return questions, None

            if attempt < MAX_RETRIES - 1:
                continue  # retry

            return None, f"LLM output validation failed after {MAX_RETRIES} attempts: {'; '.join(errors)}"
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                continue
            return None, f"LLM API error: {str(e)}"

    return None, "Unexpected error in LLM call"


@app.route("/api/generate-questions", methods=["POST"])
def generate_questions():
    """Generate LeetCode-style questions for a given topic."""
    data = request.get_json()
    if not data or "topic" not in data:
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    topic = data["topic"].strip()
    if not topic:
        return jsonify({"error": "Topic cannot be empty"}), 400

    questions, error = call_llm(topic)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"questions": questions})


def execute_code_safely(code: str, test_case: dict, function_name: str) -> dict:
    """Execute user code against a single test case in a restricted scope."""
    result = {"passed": False, "input": test_case["input"], "expected": test_case["expected"]}

    try:
        exec_globals = {}
        exec(code, exec_globals)  # noqa: S102

        if function_name not in exec_globals:
            result["error"] = f"Function '{function_name}' not found"
            return result

        func = exec_globals[function_name]
        args = []
        for param_name, param_value in test_case["input"].items():
            if isinstance(param_value, str):
                try:
                    args.append(ast.literal_eval(param_value))
                except (ValueError, SyntaxError):
                    args.append(param_value)
            else:
                args.append(param_value)

        actual = func(*args)
        result["actual"] = actual
        result["passed"] = actual == test_case["expected"]

    except Exception:
        result["error"] = traceback.format_exc().split("\n")[-2]

    return result


@app.route("/api/run", methods=["POST"])
def run_code():
    """Run user code against sample test cases."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    code = data.get("code", "")
    test_cases = data.get("test_cases", [])
    function_name = data.get("function_name", "")

    if not code or not function_name:
        return jsonify({"error": "Missing code or function_name"}), 400

    results = [execute_code_safely(code, tc, function_name) for tc in test_cases]
    passed = sum(1 for r in results if r["passed"])

    return jsonify({
        "results": results,
        "passed": passed,
        "total": len(results),
    })


@app.route("/api/submit", methods=["POST"])
def submit_code():
    """Submit user code - runs against all test cases (sample + hidden)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    code = data.get("code", "")
    sample_cases = data.get("sample_test_cases", [])
    hidden_cases = data.get("hidden_test_cases", [])
    function_name = data.get("function_name", "")

    if not code or not function_name:
        return jsonify({"error": "Missing code or function_name"}), 400

    all_cases = sample_cases + hidden_cases
    results = [execute_code_safely(code, tc, function_name) for tc in all_cases]
    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    # Only return details for sample test cases; hidden ones just show pass/fail count
    visible_results = results[:len(sample_cases)]

    return jsonify({
        "visible_results": visible_results,
        "passed": passed,
        "total": total,
        "accepted": passed == total,
    })


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        llm_configured = True
    else:
        llm_configured = bool(os.getenv("OPENAI_API_KEY"))
    return jsonify({"status": "ok", "llm_configured": llm_configured, "llm_provider": provider})


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true", port=5000)
