"""Tests for the backend prompts and app."""

import json
import pytest
from prompts import (
    build_user_prompt,
    parse_llm_response,
    validate_question,
    validate_questions,
)

# --- Prompt tests ---

def test_build_user_prompt_includes_topic():
    prompt = build_user_prompt("linked list")
    assert "linked list" in prompt


def test_build_user_prompt_nonempty():
    prompt = build_user_prompt("stack")
    assert len(prompt) > 10


# --- Validation tests ---

VALID_QUESTION = {
    "id": 1,
    "title": "Two Sum",
    "difficulty": "Easy",
    "description": "Given an array, find two numbers that add up to target.",
    "examples": [
        {"input": "nums = [2,7,11,15], target = 9", "output": "[0, 1]", "explanation": "nums[0] + nums[1] = 9"}
    ],
    "constraints": ["2 <= nums.length <= 10^4"],
    "function_name": "two_sum",
    "parameters": [{"name": "nums", "type": "List[int]"}, {"name": "target", "type": "int"}],
    "return_type": "List[int]",
    "sample_test_cases": [
        {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
        {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
        {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
    ],
    "hidden_test_cases": [
        {"input": {"nums": [1, 2], "target": 3}, "expected": [0, 1]},
        {"input": {"nums": [1, 3], "target": 4}, "expected": [0, 1]},
        {"input": {"nums": [2, 5], "target": 7}, "expected": [0, 1]},
        {"input": {"nums": [4, 6], "target": 10}, "expected": [0, 1]},
        {"input": {"nums": [1, 9], "target": 10}, "expected": [0, 1]},
        {"input": {"nums": [5, 5], "target": 10}, "expected": [0, 1]},
        {"input": {"nums": [0, 1], "target": 1}, "expected": [0, 1]},
    ],
    "starter_code": "def two_sum(nums: list[int], target: int) -> list[int]:\n    \"\"\"Find indices.\"\"\"\n    pass"
}


def test_validate_valid_question():
    errors = validate_question(VALID_QUESTION)
    assert errors == []


def test_validate_missing_field():
    q = {k: v for k, v in VALID_QUESTION.items() if k != "title"}
    errors = validate_question(q)
    assert any("title" in e for e in errors)


def test_validate_invalid_difficulty():
    q = {**VALID_QUESTION, "difficulty": "Super Hard"}
    errors = validate_question(q)
    assert any("difficulty" in e.lower() for e in errors)


def test_validate_too_few_sample_cases():
    q = {**VALID_QUESTION, "sample_test_cases": [{"input": {}, "expected": 0}]}
    errors = validate_question(q)
    assert any("sample" in e.lower() for e in errors)


def test_validate_too_few_hidden_cases():
    q = {**VALID_QUESTION, "hidden_test_cases": [{"input": {}, "expected": 0}]}
    errors = validate_question(q)
    assert any("hidden" in e.lower() for e in errors)


def test_validate_invalid_starter_code():
    q = {**VALID_QUESTION, "starter_code": "not a function"}
    errors = validate_question(q)
    assert any("starter_code" in e for e in errors)


def test_validate_questions_not_list():
    errors = validate_questions("not a list")
    assert len(errors) > 0


def test_validate_questions_empty():
    errors = validate_questions([])
    assert len(errors) > 0


def test_validate_questions_valid():
    errors = validate_questions([VALID_QUESTION])
    assert errors == []


# --- Parse LLM response tests ---

def test_parse_valid_json():
    text = json.dumps([VALID_QUESTION])
    questions, errors = parse_llm_response(text)
    assert questions is not None
    assert errors == []
    assert len(questions) == 1


def test_parse_json_with_code_fences():
    text = "```json\n" + json.dumps([VALID_QUESTION]) + "\n```"
    questions, errors = parse_llm_response(text)
    assert questions is not None
    assert errors == []


def test_parse_invalid_json():
    questions, errors = parse_llm_response("not json at all")
    assert questions is None
    assert any("Invalid JSON" in e for e in errors)


def test_parse_valid_json_but_invalid_schema():
    text = json.dumps([{"id": 1}])  # missing fields
    questions, errors = parse_llm_response(text)
    assert questions is None
    assert len(errors) > 0


# --- Flask app tests ---

@pytest.fixture
def client():
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def _add_backend_to_path():
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))


def test_get_llm_client_ollama(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    from app import get_llm_client
    client, model, error = get_llm_client()
    assert client is not None
    assert model == "llama3.2"
    assert error is None


def test_get_llm_client_openai_no_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from app import get_llm_client
    client, model, error = get_llm_client()
    assert client is None
    assert error is not None
    assert "OPENAI_API_KEY" in error


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert "llm_provider" in data


def test_health_endpoint_ollama_provider(client, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["llm_provider"] == "ollama"
    assert data["llm_configured"] is True


def test_health_endpoint_openai_no_key(client, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["llm_provider"] == "openai"
    assert data["llm_configured"] is False


def test_generate_missing_topic(client):
    resp = client.post("/api/generate-questions", json={})
    assert resp.status_code == 400


def test_generate_empty_topic(client):
    resp = client.post("/api/generate-questions", json={"topic": "  "})
    assert resp.status_code == 400


def test_run_missing_body(client):
    resp = client.post("/api/run", json={})
    assert resp.status_code == 400


def test_run_code_success(client):
    code = "def add(a, b):\n    return a + b"
    test_cases = [
        {"input": {"a": 1, "b": 2}, "expected": 3},
        {"input": {"a": 0, "b": 0}, "expected": 0},
        {"input": {"a": -1, "b": 1}, "expected": 0},
    ]
    resp = client.post("/api/run", json={
        "code": code,
        "test_cases": test_cases,
        "function_name": "add",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["passed"] == 3
    assert data["total"] == 3


def test_run_code_failure(client):
    code = "def add(a, b):\n    return a - b"
    test_cases = [{"input": {"a": 1, "b": 2}, "expected": 3}]
    resp = client.post("/api/run", json={
        "code": code,
        "test_cases": test_cases,
        "function_name": "add",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["passed"] == 0


def test_run_code_runtime_error(client):
    code = "def broken(x):\n    return 1 / 0"
    test_cases = [{"input": {"x": 1}, "expected": 0}]
    resp = client.post("/api/run", json={
        "code": code,
        "test_cases": test_cases,
        "function_name": "broken",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["passed"] == 0
    assert "error" in data["results"][0]


def test_submit_code(client):
    code = "def add(a, b):\n    return a + b"
    sample = [{"input": {"a": 1, "b": 2}, "expected": 3}]
    hidden = [{"input": {"a": 3, "b": 4}, "expected": 7}]
    resp = client.post("/api/submit", json={
        "code": code,
        "sample_test_cases": sample,
        "hidden_test_cases": hidden,
        "function_name": "add",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["accepted"] is True
    assert data["passed"] == 2
    assert data["total"] == 2
