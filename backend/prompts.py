"""LLM prompt templates and validation for generating LeetCode-style questions."""

import json

SYSTEM_PROMPT = """You are an expert algorithm and data structure instructor. 
You generate LeetCode-style coding problems. You MUST respond with valid JSON only, no markdown or extra text.

Your output must be a JSON array of problem objects. Each problem object must have this exact schema:
{
  "id": <integer>,
  "title": "<string>",
  "difficulty": "<Easy|Medium|Hard>",
  "description": "<string - detailed problem description in plain text>",
  "examples": [
    {
      "input": "<string>",
      "output": "<string>",
      "explanation": "<string>"
    }
  ],
  "constraints": ["<string>", ...],
  "function_name": "<string - the Python function name to implement>",
  "parameters": [
    {"name": "<string>", "type": "<string - Python type hint>"}
  ],
  "return_type": "<string - Python type hint>",
  "sample_test_cases": [
    {"input": {"<param_name>": <value>, ...}, "expected": <value>}
  ],
  "hidden_test_cases": [
    {"input": {"<param_name>": <value>, ...}, "expected": <value>}
  ],
  "starter_code": "<string - Python function signature with docstring>"
}

Rules:
1. Generate exactly 3 problems: one Easy, one Medium, one Hard.
2. Each problem must have exactly 2 examples with explanations.
3. Each problem must have 3-5 constraints.
4. Each problem must have exactly 3 sample_test_cases (visible to user) and exactly 10 hidden_test_cases (for submission).
5. Test case inputs must be valid Python literals that can be parsed with ast.literal_eval.
6. The starter_code must be a valid Python function with type hints and a docstring.
7. All problems must be related to the requested data structure/topic.
8. Respond ONLY with the JSON array. No markdown, no code fences, no commentary."""


def build_user_prompt(topic: str) -> str:
    """Build the user prompt for the LLM."""
    return (
        f"Generate 3 LeetCode-style coding problems about: {topic}\n\n"
        f"Focus on practical usage of {topic} in algorithm design. "
        f"Include problems that cover fundamental operations, "
        f"common patterns, and an advanced application."
    )


def validate_question(question: dict) -> list[str]:
    """Validate a single question object. Returns a list of error messages."""
    errors = []
    required_fields = [
        "id", "title", "difficulty", "description", "examples",
        "constraints", "function_name", "parameters", "return_type",
        "sample_test_cases", "hidden_test_cases", "starter_code"
    ]
    for field in required_fields:
        if field not in question:
            errors.append(f"Missing required field: {field}")

    if "difficulty" in question and question["difficulty"] not in ("Easy", "Medium", "Hard"):
        errors.append(f"Invalid difficulty: {question['difficulty']}")

    if "examples" in question:
        if not isinstance(question["examples"], list) or len(question["examples"]) < 1:
            errors.append("Must have at least 1 example")

    if "sample_test_cases" in question:
        if not isinstance(question["sample_test_cases"], list) or len(question["sample_test_cases"]) < 3:
            errors.append("Must have at least 3 sample test cases")

    if "hidden_test_cases" in question:
        if not isinstance(question["hidden_test_cases"], list) or len(question["hidden_test_cases"]) < 7:
            errors.append("Must have at least 7 hidden test cases")

    if "starter_code" in question:
        if not isinstance(question["starter_code"], str) or "def " not in question["starter_code"]:
            errors.append("starter_code must be a valid Python function")

    return errors


def validate_questions(questions: list) -> list[str]:
    """Validate the full list of generated questions."""
    errors = []
    if not isinstance(questions, list):
        return ["Response must be a JSON array of questions"]
    if len(questions) < 1:
        return ["Must generate at least 1 question"]

    for i, q in enumerate(questions):
        q_errors = validate_question(q)
        for err in q_errors:
            errors.append(f"Question {i + 1}: {err}")

    return errors


def parse_llm_response(response_text: str) -> tuple[list | None, list[str]]:
    """Parse and validate the LLM response. Returns (questions, errors)."""
    text = response_text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # remove opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    try:
        questions = json.loads(text)
    except json.JSONDecodeError as e:
        return None, [f"Invalid JSON from LLM: {e}"]

    errors = validate_questions(questions)
    if errors:
        return None, errors

    return questions, []
