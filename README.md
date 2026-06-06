# 🧠 NeoMind AI
### Intelligent Multi-Mode Conversational AI Agent
> Built for NEOSTATS Innovation Sprint — Christ (Deemed to be University), June 2026

---

## Overview

NeoMind is an intelligent conversational AI agent that answers questions through multiple knowledge sources while maintaining conversational context.

The agent intelligently decides whether to:
- 🧠 Answer directly using LLM knowledge
- 🌐 Search the web for real-time information
- 📄 Retrieve information from documents using RAG
- 💬 Use conversation memory for follow-up questions

---

## Features

| Mode | Description | Status |
|------|-------------|--------|
| 🧠 General Chat | LLM answers directly via Groq | ✅ |
| 🌐 Web Search | Live DuckDuckGo search results | ✅ |
| 📄 RAG Mode | Document retrieval via FAISS | 🔄 |
| 💬 Memory | Multi-turn conversation context | ✅ |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Agent Framework | LangGraph |
| LLM | Groq (Llama 3 8B) |
| Web Search | DuckDuckGo Search |
| Vector DB | FAISS |
| Embeddings | HuggingFace (BGE Small) |
| Backend | Python 3.13 |

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/k-khushi07/NeoMindAI
cd NeoMindAI
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key
Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_api_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

### 5. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## Project Structure

```
NeoMindAI/
├── app.py              # Streamlit UI + agent integration
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

---

## Team

Built by Team NeoMind — Christ University, Department of Computer Science

---

## License
MIT
