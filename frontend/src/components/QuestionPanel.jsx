import './QuestionPanel.css';

export default function QuestionPanel({ question }) {
  if (!question) return null;

  const difficultyClass = `difficulty-${question.difficulty.toLowerCase()}`;

  return (
    <div className="question-panel">
      <div className="question-header">
        <h2 className="question-title">{question.id}. {question.title}</h2>
        <span className={`difficulty-badge ${difficultyClass}`}>{question.difficulty}</span>
      </div>

      <div className="question-description">
        <p>{question.description}</p>
      </div>

      <div className="question-examples">
        {question.examples.map((ex, i) => (
          <div key={i} className="example-block">
            <h4>Example {i + 1}:</h4>
            <div className="example-content">
              <p><strong>Input:</strong> {ex.input}</p>
              <p><strong>Output:</strong> {ex.output}</p>
              {ex.explanation && <p><strong>Explanation:</strong> {ex.explanation}</p>}
            </div>
          </div>
        ))}
      </div>

      <div className="question-constraints">
        <h4>Constraints:</h4>
        <ul>
          {question.constraints.map((c, i) => (
            <li key={i}>{c}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
