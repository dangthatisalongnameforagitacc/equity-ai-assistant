import { useState, useRef, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

export default function ChatPanel({ externalQuestion, onQuestionConsumed }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Handle external question from sidebar
  useEffect(() => {
    if (externalQuestion) {
      handleSend(externalQuestion);
      onQuestionConsumed();
    }
  }, [externalQuestion]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Auto-resize textarea
  const handleTextareaChange = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  const handleSend = async (questionOverride) => {
    const question = questionOverride || input.trim();
    if (!question || isLoading) return;

    // Add user message
    const userMessage = { role: 'user', content: question };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: '⚠️ Sorry, I encountered an error processing your question. Please make sure the backend server is running on port 8000.',
        sources: [],
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  // Format message text with basic markdown
  const formatContent = (text) => {
    // Split into paragraphs
    const paragraphs = text.split('\n\n');
    return paragraphs.map((para, i) => {
      // Handle bullet points
      if (para.includes('\n- ') || para.startsWith('- ')) {
        const items = para.split('\n').filter(l => l.trim());
        return (
          <ul key={i}>
            {items.map((item, j) => (
              <li key={j}>{item.replace(/^-\s*/, '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').split('<strong>').map((part, k) => {
                if (part.includes('</strong>')) {
                  const [bold, rest] = part.split('</strong>');
                  return <span key={k}><strong>{bold}</strong>{rest}</span>;
                }
                return part;
              })}</li>
            ))}
          </ul>
        );
      }

      // Handle numbered lists
      if (para.match(/^\d+\./)) {
        const items = para.split('\n').filter(l => l.trim());
        return (
          <ol key={i}>
            {items.map((item, j) => (
              <li key={j}>{item.replace(/^\d+\.\s*/, '')}</li>
            ))}
          </ol>
        );
      }

      // Regular paragraph with bold handling
      return <p key={i}>{para.split(/\*\*(.*?)\*\*/g).map((part, k) =>
        k % 2 === 1 ? <strong key={k}>{part}</strong> : part
      )}</p>;
    });
  };

  const [expandedSources, setExpandedSources] = useState({});

  const toggleSources = (msgIndex) => {
    setExpandedSources(prev => ({
      ...prev,
      [msgIndex]: !prev[msgIndex],
    }));
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-header">
        <h2>💬 Equity AI Assistant</h2>
        <div className="header-actions">
          {messages.length > 0 && (
            <button className="header-btn" onClick={clearChat}>
              🗑️ Clear Chat
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 && !isLoading ? (
          <WelcomeScreen onCardClick={handleSend} />
        ) : (
          <>
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'assistant' ? '⚡' : '👤'}
                </div>
                <div className="message-content">
                  <div className="message-bubble">
                    {formatContent(msg.content)}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="message-sources">
                      <div
                        className="sources-header"
                        onClick={() => toggleSources(i)}
                      >
                        📎 {msg.sources.length} Source{msg.sources.length > 1 ? 's' : ''} Referenced
                        {expandedSources[i] ? ' ▼' : ' ▶'}
                      </div>
                      {expandedSources[i] && msg.sources.map((src, j) => (
                        <div key={j} className="source-item">
                          <span className="source-badge">📄 {src.document}</span>
                          <span className="source-snippet">{src.relevance_snippet}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="typing-indicator">
                <div className="message-avatar" style={{
                  background: 'linear-gradient(135deg, var(--primary-500), var(--primary-700))',
                  width: 36, height: 36, borderRadius: 12,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16
                }}>⚡</div>
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about ESOPs, vesting, cap tables, or equity..."
            rows={1}
            disabled={isLoading}
          />
          <button
            className="send-btn"
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
          >
            ➤
          </button>
        </div>
        <div className="chat-input-hint">
          Press Enter to send · Shift+Enter for new line
        </div>
      </div>
    </div>
  );
}

function WelcomeScreen({ onCardClick }) {
  const cards = [
    { icon: '📊', title: 'ESOP Policy', desc: 'Vesting schedules, exercise windows, eligibility', q: 'What is the vesting schedule for new employees?' },
    { icon: '📈', title: 'Cap Table', desc: 'Funding rounds, shareholding, dilution analysis', q: 'How much dilution occurred in Series B?' },
    { icon: '📋', title: 'Board Resolutions', desc: 'ESOP pool expansion, governance decisions', q: 'What did the board resolve about ESOP pool expansion?' },
    { icon: '❓', title: 'Vesting FAQ', desc: 'Resignation, termination, acceleration rules', q: 'What happens to my options if I resign?' },
  ];

  return (
    <div className="welcome-screen">
      <div className="welcome-icon">⚡</div>
      <h2>Equity AI Assistant</h2>
      <p>
        Ask me anything about ESOPs, cap tables, vesting schedules, and equity management.
        I'll answer based on your uploaded documents with source citations.
      </p>
      <div className="welcome-cards">
        {cards.map((card, i) => (
          <div
            key={i}
            className="welcome-card"
            onClick={() => onCardClick(card.q)}
          >
            <div className="card-icon">{card.icon}</div>
            <h4>{card.title}</h4>
            <p>{card.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
