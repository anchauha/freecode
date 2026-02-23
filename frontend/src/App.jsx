import { useState } from 'react';
import TopicInput from './components/TopicInput';
import QuestionNav from './components/QuestionNav';
import QuestionPanel from './components/QuestionPanel';
import CodeEditor from './components/CodeEditor';
import TestResults from './components/TestResults';
import { generateQuestions, runCode, submitCode } from './api';
import './App.css';

export default function App() {
  const [questions, setQuestions] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [codes, setCodes] = useState({});
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState(null);
  const [resultType, setResultType] = useState(null);
  const [error, setError] = useState(null);

  const currentQuestion = questions ? questions[activeIndex] : null;
  const currentCode = currentQuestion ? (codes[currentQuestion.id] ?? currentQuestion.starter_code) : '';

  const handleGenerate = async (topic) => {
    setLoading(true);
    setError(null);
    try {
      const data = await generateQuestions(topic);
      setQuestions(data.questions);
      setActiveIndex(0);
      setCodes({});
      setResults(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCodeChange = (code) => {
    if (currentQuestion) {
      setCodes((prev) => ({ ...prev, [currentQuestion.id]: code }));
    }
  };

  const handleRun = async () => {
    if (!currentQuestion) return;
    setRunning(true);
    setResults(null);
    setError(null);
    try {
      const data = await runCode(
        currentCode,
        currentQuestion.sample_test_cases,
        currentQuestion.function_name,
      );
      setResults(data);
      setResultType('run');
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!currentQuestion) return;
    setSubmitting(true);
    setResults(null);
    setError(null);
    try {
      const data = await submitCode(
        currentCode,
        currentQuestion.sample_test_cases,
        currentQuestion.hidden_test_cases,
        currentQuestion.function_name,
      );
      setResults(data);
      setResultType('submit');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    setQuestions(null);
    setActiveIndex(0);
    setCodes({});
    setResults(null);
    setError(null);
  };

  const handleSelectQuestion = (index) => {
    setActiveIndex(index);
    setResults(null);
    setError(null);
  };

  if (!questions) {
    return (
      <div className="app">
        <TopicInput onGenerate={handleGenerate} loading={loading} />
        {error && <p className="global-error">{error}</p>}
      </div>
    );
  }

  return (
    <div className="app workspace">
      <QuestionNav
        questions={questions}
        activeIndex={activeIndex}
        onSelect={handleSelectQuestion}
        onBack={handleBack}
      />
      <div className="workspace-body">
        <div className="left-panel">
          <QuestionPanel question={currentQuestion} />
        </div>
        <div className="right-panel">
          <div className="editor-section">
            <CodeEditor code={currentCode} onChange={handleCodeChange} />
          </div>
          <div className="action-bar">
            <button className="run-btn" onClick={handleRun} disabled={running || submitting}>
              {running ? 'Running...' : '▶ Run'}
            </button>
            <button className="submit-btn" onClick={handleSubmit} disabled={running || submitting}>
              {submitting ? 'Submitting...' : '⬆ Submit'}
            </button>
          </div>
          <div className="results-section">
            {error && <p className="panel-error">{error}</p>}
            <TestResults results={results} type={resultType} />
          </div>
        </div>
      </div>
    </div>
  );
}
