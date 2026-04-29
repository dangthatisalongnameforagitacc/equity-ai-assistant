import { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatPanel from './components/ChatPanel';
import DocumentPanel from './components/DocumentPanel';
import './index.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [pendingQuestion, setPendingQuestion] = useState(null);

  const handleQuestionClick = (question) => {
    setActiveTab('chat');
    setPendingQuestion(question);
  };

  return (
    <div className="app-layout">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onQuestionClick={handleQuestionClick}
      />

      <main className="main-content">
        {activeTab === 'chat' ? (
          <ChatPanel
            externalQuestion={pendingQuestion}
            onQuestionConsumed={() => setPendingQuestion(null)}
          />
        ) : (
          <DocumentPanel />
        )}
      </main>
    </div>
  );
}
