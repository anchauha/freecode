import './TestResults.css';

export default function TestResults({ results, type }) {
  if (!results) return null;

  const { passed, total } = results;
  const allPassed = passed === total;
  const items = type === 'run' ? results.results : results.visible_results;

  return (
    <div className="test-results">
      <div className={`results-summary ${allPassed ? 'all-passed' : 'some-failed'}`}>
        {type === 'submit' && results.accepted && (
          <span className="accepted-badge">✓ Accepted</span>
        )}
        {type === 'submit' && !results.accepted && (
          <span className="rejected-badge">✗ Not Accepted</span>
        )}
        <span className="results-count">{passed}/{total} test cases passed</span>
      </div>

      {items && items.map((tc, i) => (
        <div key={i} className={`test-case-result ${tc.passed ? 'passed' : 'failed'}`}>
          <div className="tc-header">
            <span className={`tc-status ${tc.passed ? 'passed' : 'failed'}`}>
              {tc.passed ? '✓' : '✗'} Test Case {i + 1}
            </span>
          </div>
          <div className="tc-details">
            <p><strong>Input:</strong> {JSON.stringify(tc.input)}</p>
            <p><strong>Expected:</strong> {JSON.stringify(tc.expected)}</p>
            {tc.actual !== undefined && (
              <p><strong>Actual:</strong> {JSON.stringify(tc.actual)}</p>
            )}
            {tc.error && (
              <p className="tc-error"><strong>Error:</strong> {tc.error}</p>
            )}
          </div>
        </div>
      ))}

      {type === 'submit' && items && items.length < total && (
        <p className="hidden-info">
          + {total - items.length} hidden test cases ({passed - items.filter(t => t.passed).length} passed)
        </p>
      )}
    </div>
  );
}
