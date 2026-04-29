import { useState } from 'react';

const SUGGESTED_QUESTIONS = [
  "What is the vesting schedule for new employees?",
  "How much dilution occurred in Series B?",
  "What happens to my options if I resign?",
  "What is the current ESOP pool size?",
  "Explain single vs double trigger acceleration",
  "What are the tax implications of exercising options?",
  "Who approved the ESOP pool expansion?",
  "What is the current share price / FMV?",
];

export default function Sidebar({ activeTab, setActiveTab, onQuestionClick }) {
  return (
    <aside className="sidebar">
      {/* Header / Branding */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">⚡</div>
          <div>
            <h1>EquityAI</h1>
            <div className="subtitle">RAG Assistant</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <button
          className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <span className="nav-icon">💬</span>
          <span>Chat</span>
        </button>
        <button
          className={`nav-item ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          <span className="nav-icon">📄</span>
          <span>Documents</span>
        </button>
      </nav>

      {/* Suggested Questions */}
      {activeTab === 'chat' && (
        <div className="sidebar-suggestions">
          <div className="suggestions-title">Try Asking</div>
          {SUGGESTED_QUESTIONS.map((q, i) => (
            <button
              key={i}
              className="suggestion-item"
              onClick={() => onQuestionClick(q)}
            >
              <span className="q-icon">→</span>
              <span>{q}</span>
            </button>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="status-badge">
          <span className="status-dot"></span>
          <span>Powered by Gemini + LangChain</span>
        </div>
      </div>
    </aside>
  );
}
