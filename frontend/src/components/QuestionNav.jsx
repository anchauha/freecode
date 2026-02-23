import './QuestionNav.css';

export default function QuestionNav({ questions, activeIndex, onSelect, onBack }) {
  return (
    <div className="question-nav">
      <button className="nav-back-btn" onClick={onBack}>← New Topic</button>
      <div className="nav-tabs">
        {questions.map((q, i) => (
          <button
            key={q.id}
            className={`nav-tab ${i === activeIndex ? 'active' : ''} difficulty-${q.difficulty.toLowerCase()}`}
            onClick={() => onSelect(i)}
          >
            {q.id}. {q.title}
            <span className="nav-diff">{q.difficulty}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
