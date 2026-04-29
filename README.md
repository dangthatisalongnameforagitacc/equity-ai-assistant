# EquityAI — RAG-Powered Equity Management Assistant

A full-stack AI assistant that uses **Retrieval-Augmented Generation (RAG)** to answer questions about equity management, ESOPs, cap tables, and corporate governance — powered by **LangChain**, **Google Gemini**, and **ChromaDB**.

## 🎯 What This Does

- **Intelligent Q&A**: Ask natural language questions about equity documents and get accurate, source-grounded answers
- **Source Citations**: Every answer includes references to the specific documents used
- **Document Management**: Upload your own PDF/TXT documents to expand the knowledge base
- **Conversation Memory**: Multi-turn conversations with context awareness
- **Pre-loaded Knowledge**: Ships with sample ESOP policy, cap table, board resolution, and vesting FAQ documents

## 🏗️ Architecture

```
┌──────────────────────┐     ┌──────────────────────────────┐
│   React Frontend     │────▶│   FastAPI Backend             │
│   (Vite + React)     │◀────│                              │
│                      │     │  ┌─────────────────────────┐  │
│  • Chat UI           │     │  │  LangChain RAG Pipeline │  │
│  • Document Upload   │     │  │  ┌───────┐ ┌─────────┐ │  │
│  • Source Citations   │     │  │  │Gemini │ │ChromaDB │ │  │
│  • Welcome Dashboard │     │  │  │ LLM   │ │Vectors  │ │  │
│                      │     │  │  └───────┘ └─────────┘ │  │
└──────────────────────┘     │  └─────────────────────────┘  │
                             └──────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Google Gemini 2.0 Flash |
| **RAG Framework** | LangChain |
| **Vector Store** | ChromaDB |
| **Backend** | Python, FastAPI |
| **Frontend** | React, Vite |
| **Embeddings** | Google Generative AI Embeddings |

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Gemini API Key (free at [aistudio.google.com](https://aistudio.google.com))

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux.  On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 3. Open the App
- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

## 📄 Sample Documents

The app comes pre-loaded with realistic equity management documents:

| Document | Description |
|----------|-------------|
| `esop_policy_2024.txt` | Full ESOP policy with vesting, exercise, tax rules |
| `cap_table_summary.txt` | Cap table with 5 funding rounds and dilution analysis |
| `board_resolution.txt` | Board resolution for ESOP pool expansion |
| `vesting_schedule_faq.txt` | 15 FAQs about vesting, termination, acceleration |

## 💡 Example Questions

- "What is the vesting schedule for new employees?"
- "How much dilution occurred in Series B?"
- "What happens to my options if I resign?"
- "What is the current ESOP pool size and how much is available?"
- "Explain single vs double trigger acceleration"
- "What are the tax implications of exercising options?"
- "Who approved the ESOP pool expansion and what was the vote?"

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send a question and get an AI answer |
| `GET` | `/api/chat/history/{session_id}` | Get chat history |
| `DELETE` | `/api/chat/history/{session_id}` | Clear chat history |
| `GET` | `/api/documents` | List all documents |
| `POST` | `/api/documents/upload` | Upload a new document |
| `DELETE` | `/api/documents/{doc_id}` | Delete a document |
| `GET` | `/api/health` | Health check with doc count |

## 🏛️ Project Structure

```
RAG pipeline/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── rag/
│   │   │   ├── ingestion.py     # Document processing & embedding
│   │   │   └── retriever.py     # RAG query pipeline
│   │   └── routes/
│   │       ├── chat.py          # Chat API endpoints
│   │       └── documents.py     # Document management API
│   ├── data/
│   │   └── sample_docs/         # Pre-loaded equity documents
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main application
    │   ├── components/
    │   │   ├── Sidebar.jsx      # Navigation & suggestions
    │   │   ├── ChatPanel.jsx    # Chat interface
    │   │   └── DocumentPanel.jsx # Document management
    │   ├── index.css            # Design system
    │   └── main.jsx             # Entry point
    └── index.html
```

## 📝 License

MIT
