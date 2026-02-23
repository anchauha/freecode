import Editor from '@monaco-editor/react';
import './CodeEditor.css';

export default function CodeEditor({ code, onChange }) {
  return (
    <div className="code-editor">
      <div className="editor-header">
        <span className="editor-lang">Python 3</span>
      </div>
      <div className="editor-wrapper">
        <Editor
          height="100%"
          language="python"
          theme="vs-dark"
          value={code}
          onChange={(value) => onChange(value || '')}
          options={{
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            wordWrap: 'on',
          }}
        />
      </div>
    </div>
  );
}
