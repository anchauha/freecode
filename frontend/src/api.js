const API_BASE = '/api';

export async function generateQuestions(topic) {
  const res = await fetch(`${API_BASE}/generate-questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to generate questions');
  }
  return res.json();
}

export async function runCode(code, testCases, functionName) {
  const res = await fetch(`${API_BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code,
      test_cases: testCases,
      function_name: functionName,
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to run code');
  }
  return res.json();
}

export async function submitCode(code, sampleTestCases, hiddenTestCases, functionName) {
  const res = await fetch(`${API_BASE}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code,
      sample_test_cases: sampleTestCases,
      hidden_test_cases: hiddenTestCases,
      function_name: functionName,
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to submit code');
  }
  return res.json();
}
