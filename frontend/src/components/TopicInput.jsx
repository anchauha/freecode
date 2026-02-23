import { useState } from 'react';
import './TopicInput.css';

export default function TopicInput({ onGenerate, loading }) {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim()) {
      onGenerate(topic.trim());
    }
  };

  return (
    <div className="topic-input-container">
      <h1 className="app-title">FreeCode</h1>
      <p className="app-subtitle">Learn Data Structures with LeetCode-Style Problems</p>
      <form className="topic-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="topic-field"
          placeholder="Enter a data structure (e.g., Linked List, Binary Tree, Stack...)"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="generate-btn" disabled={loading || !topic.trim()}>
          {loading ? 'Generating...' : 'Generate Problems'}
        </button>
      </form>
      {loading && <p className="loading-text">Generating LeetCode-style problems with AI... This may take a moment.</p>}
    </div>
  );
}
