import streamlit as st
import time

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeoMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Global */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  .stApp {
    background-color: #09090b;
    color: #fafafa;
  }

  /* Hide default streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background-color: #111113 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
  }

  [data-testid="stSidebar"] * {
    color: #a1a1aa !important;
  }

  /* Mode buttons */
  .stButton > button {
    width: 100%;
    background: transparent;
    border: 1px solid rgba(255,255,255,0.08);
    color: #a1a1aa;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.15s;
    text-align: left;
  }

  .stButton > button:hover {
    background: rgba(99,102,241,0.1);
    border-color: rgba(99,102,241,0.3);
    color: #818cf8;
  }

  /* Chat messages */
  .user-bubble {
    display: flex;
    justify-content: flex-end;
    margin: 12px 0;
  }

  .user-bubble .bubble {
    background: #6366f1;
    color: #fff;
    padding: 10px 16px;
    border-radius: 18px 18px 4px 18px;
    max-width: 70%;
    font-size: 14px;
    line-height: 1.6;
  }

  .agent-bubble {
    display: flex;
    justify-content: flex-start;
    margin: 12px 0;
    gap: 10px;
    align-items: flex-start;
  }

  .agent-avatar {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }

  .agent-bubble .bubble {
    background: #18181b;
    color: #e4e4e7;
    padding: 12px 16px;
    border-radius: 4px 18px 18px 18px;
    max-width: 75%;
    font-size: 14px;
    line-height: 1.7;
    border: 1px solid rgba(255,255,255,0.06);
  }

  .mode-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    margin-bottom: 6px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  .badge-llm    { background: rgba(99,102,241,0.15); color: #818cf8; }
  .badge-web    { background: rgba(16,185,129,0.15); color: #34d399; }
  .badge-rag    { background: rgba(245,158,11,0.15); color: #fbbf24; }

  .source-card {
    background: #1c1c1f;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 8px;
    font-size: 12px;
    color: #71717a;
  }

  .source-card a { color: #818cf8; text-decoration: none; }

  /* Input */
  .stChatInput textarea {
    background: #18181b !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #fafafa !important;
    border-radius: 12px !important;
    font-size: 14px !important;
  }

  /* Divider */
  hr { border-color: rgba(255,255,255,0.06) !important; }

  /* Metric cards */
  .metric-card {
    background: #111113;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
  }
  .metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #fafafa;
  }
  .metric-label {
    font-size: 11px;
    color: #52525b;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* Section header */
  .section-header {
    font-size: 11px;
    font-weight: 600;
    color: #3f3f46;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 16px 0 8px;
    padding: 0 4px;
  }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "general"

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []


# ─── Helpers ─────────────────────────────────────────────────────────────────
MODE_META = {
    "general": {"label": "General Chat",  "badge": "badge-llm", "tag": "LLM",        "icon": "🧠", "desc": "LLM answers directly"},
    "web":     {"label": "Web Search",    "badge": "badge-web", "tag": "WEB SEARCH",  "icon": "🌐", "desc": "Searches the internet"},
    "rag":     {"label": "RAG Mode",      "badge": "badge-rag", "tag": "RAG",         "icon": "📄", "desc": "Searches your documents"},
}

def render_message(msg):
    role = msg["role"]
    content = msg["content"]
    mode = msg.get("mode", "general")
    sources = msg.get("sources", [])
    meta = MODE_META[mode]

    if role == "user":
        st.markdown(f"""
        <div class="user-bubble">
          <div class="bubble">{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        sources_html = ""
        if sources:
            sources_html = "".join([
                f'<div class="source-card">📎 <a href="{s.get("url","#")}" target="_blank">{s.get("title", s.get("url","Source"))}</a></div>'
                for s in sources
            ])

        st.markdown(f"""
        <div class="agent-bubble">
          <div class="agent-avatar">🧠</div>
          <div>
            <span class="mode-badge {meta['badge']}">{meta['tag']}</span>
            <div class="bubble">{content}{sources_html}</div>
          </div>
        </div>""", unsafe_allow_html=True)


def placeholder_response(query, mode):
    """
    PLACEHOLDER — replace this function with your actual agent call.
    Your teammate should replace this with:
        from agent import run_agent
        return run_agent(query, mode, st.session_state.messages)
    """
    time.sleep(0.8)  # simulate latency

    responses = {
        "general": (
            f"This is a <b>General Chat</b> response to: <i>{query}</i><br><br>"
            "The LLM will answer this directly without using any external tools. "
            "Connect your Groq/Ollama model here.",
            []
        ),
        "web": (
            f"Searching the web for: <i>{query}</i><br><br>"
            "🔍 Top results would appear here after DuckDuckGo search. "
            "Connect your web search tool to replace this placeholder.",
            [{"title": "Example Result — Wikipedia", "url": "https://wikipedia.org"},
             {"title": "Example Result — News Article", "url": "https://news.ycombinator.com"}]
        ),
        "rag": (
            f"Searching uploaded documents for: <i>{query}</i><br><br>"
            "📄 Relevant chunks from your FAISS vector store would appear here. "
            "Connect your RAG pipeline to replace this placeholder.",
            [{"title": "Uploaded Document — Chunk 1", "url": "#"},
             {"title": "Uploaded Document — Chunk 2", "url": "#"}]
        ),
    }
    return responses[mode]


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 4px 16px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
        <div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:18px;">🧠</div>
        <div>
          <div style="font-size:15px;font-weight:700;color:#fafafa !important;">NeoMind AI</div>
          <div style="font-size:11px;color:#52525b !important;">Intelligent Agent</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Mode</div>', unsafe_allow_html=True)

    for key, meta in MODE_META.items():
        active = "✓ " if st.session_state.mode == key else ""
        if st.button(f"{meta['icon']}  {active}{meta['label']}", key=f"btn_{key}"):
            st.session_state.mode = key
            st.rerun()

    st.markdown('<div class="section-header">Documents</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload for RAG",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded:
        for f in uploaded:
            if f.name not in st.session_state.uploaded_docs:
                st.session_state.uploaded_docs.append(f.name)
        st.success(f"{len(uploaded)} file(s) ready")

    if st.session_state.uploaded_docs:
        for doc in st.session_state.uploaded_docs:
            st.markdown(f'<div class="source-card">📄 {doc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Session</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value">{len(st.session_state.messages)}</div>
          <div class="metric-label">Messages</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value">{len(st.session_state.uploaded_docs)}</div>
          <div class="metric-label">Docs</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑  Clear Chat", key="clear"):
        st.session_state.messages = []
        st.rerun()


# ─── Main Area ───────────────────────────────────────────────────────────────
current_mode = st.session_state.mode
meta = MODE_META[current_mode]

# Header
st.markdown(f"""
<div style="padding: 24px 0 16px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 8px;">
  <div style="display:flex; align-items:center; gap:10px;">
    <span style="font-size:22px;">{meta['icon']}</span>
    <div>
      <div style="font-size:18px; font-weight:700; color:#fafafa; letter-spacing:-0.4px;">
        NeoMind — {meta['label']}
      </div>
      <div style="font-size:12px; color:#52525b; margin-top:2px;">{meta['desc']}</div>
    </div>
    <span class="mode-badge {meta['badge']}" style="margin-left:auto;">{meta['tag']}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Chat history
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color: #3f3f46;">
          <div style="font-size:40px; margin-bottom:12px;">🧠</div>
          <div style="font-size:16px; font-weight:600; color:#52525b; margin-bottom:8px;">
            Ask NeoMind anything
          </div>
          <div style="font-size:13px; color:#3f3f46;">
            Switch modes in the sidebar — General, Web Search, or RAG
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            render_message(msg)

# Input
query = st.chat_input(f"Ask in {meta['label']} mode...")

if query:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "mode": current_mode,
    })

    # Get response (replace placeholder_response with your agent call)
    with st.spinner("Thinking..."):
        response_text, sources = placeholder_response(query, current_mode)

    # Add agent message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "mode": current_mode,
        "sources": sources,
    })

    st.rerun()
