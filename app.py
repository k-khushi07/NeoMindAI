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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.stApp { background-color: #0c0c0e; color: #f0f0f2; }

#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #0f0f12 !important;
  border-right: 1px solid #1e1e24 !important;
}
[data-testid="stSidebar"] section { padding: 0 !important; }

/* ── Sidebar buttons ── */
.stButton > button {
  width: 100%;
  background: transparent !important;
  border: 1px solid #1e1e24 !important;
  color: #6b6b80 !important;
  border-radius: 10px !important;
  padding: 10px 14px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  text-align: left !important;
  transition: all 0.15s ease !important;
  letter-spacing: -0.1px !important;
}
.stButton > button:hover {
  background: rgba(99,102,241,0.08) !important;
  border-color: rgba(99,102,241,0.25) !important;
  color: #a5b4fc !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
  background: #0f0f12 !important;
  border-top: 1px solid #1e1e24 !important;
  padding: 16px 24px !important;
}
[data-testid="stChatInput"] textarea {
  background: #18181e !important;
  border: 1px solid #2a2a35 !important;
  border-radius: 12px !important;
  color: #f0f0f2 !important;
  font-size: 14px !important;
  font-family: 'Inter', sans-serif !important;
  padding: 12px 16px !important;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a35; border-radius: 4px; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #6366f1 !important; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "general"
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []


# ─── Constants ───────────────────────────────────────────────────────────────
MODE_META = {
    "general": {"label": "General Chat",  "icon": "🧠", "tag": "LLM",        "color": "#818cf8", "bg": "rgba(99,102,241,0.12)",  "desc": "Answered by LLM directly"},
    "web":     {"label": "Web Search",    "icon": "🌐", "tag": "WEB",        "color": "#34d399", "bg": "rgba(52,211,153,0.12)",  "desc": "Live results from the internet"},
    "rag":     {"label": "RAG Mode",      "icon": "📄", "tag": "RAG",        "color": "#fbbf24", "bg": "rgba(251,191,36,0.12)",  "desc": "Answers from your documents"},
}


# ─── Placeholder Backend ─────────────────────────────────────────────────────
def placeholder_response(query, mode):
    if mode == "web":
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=4))
            
            if results:
                summary = "<b>Here's what I found on the web:</b><br><br>"
                for r in results:
                    summary += f"• <b>{r['title']}</b><br>{r['body']}<br><br>"
                
                sources = [{"title": r["title"], "url": r["href"]} for r in results]
                return summary, sources
            else:
                return "No results found for that query.", []
        
        except Exception as e:
            return f"Web search failed: {str(e)}", []

    elif mode == "general":
        time.sleep(0.6)
        return (
            f"This is a <b>General Chat</b> placeholder.<br><br>"
            f"Your query: <i>\"{query}\"</i><br><br>"
            "Connect Groq LLM here to get real answers.",
            []
        )

    elif mode == "rag":
        time.sleep(0.6)
        return (
            f"Searching your documents for: <i>\"{query}\"</i><br><br>"
            "Connect FAISS + embeddings here for real RAG answers.",
            [{"title": "Uploaded Doc — Chunk 1", "url": "#"}]
        )


# ─── Render Message ───────────────────────────────────────────────────────────
def render_message(msg):
    role    = msg["role"]
    content = msg["content"]
    mode    = msg.get("mode", "general")
    sources = msg.get("sources", [])
    meta    = MODE_META[mode]

    if role == "user":
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;margin:16px 0 4px;">
          <div style="
            background: linear-gradient(135deg,#6366f1,#7c3aed);
            color:#fff;
            padding:10px 16px;
            border-radius:18px 18px 4px 18px;
            max-width:68%;
            font-size:14px;
            line-height:1.65;
            box-shadow:0 2px 12px rgba(99,102,241,0.25);
          ">{content}</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        sources_html = ""
        if sources:
            items = "".join([
                f"""<a href="{s.get('url','#')}" target="_blank" style="
                  display:block;
                  background:#1a1a22;
                  border:1px solid #2a2a35;
                  border-radius:8px;
                  padding:7px 12px;
                  margin-top:6px;
                  font-size:12px;
                  color:#818cf8;
                  text-decoration:none;
                  transition:border-color 0.15s;
                ">🔗 {s.get('title', s.get('url','Source'))}</a>"""
                for s in sources
            ])
            sources_html = f'<div style="margin-top:10px;">{items}</div>'

        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:12px;margin:16px 0 4px;">
          <div style="
            width:34px;height:34px;flex-shrink:0;
            border-radius:10px;
            background:linear-gradient(135deg,#6366f1,#7c3aed);
            display:flex;align-items:center;justify-content:center;
            font-size:17px;
            box-shadow:0 2px 8px rgba(99,102,241,0.3);
          ">🧠</div>
          <div style="max-width:74%;">
            <div style="
              display:inline-flex;align-items:center;gap:5px;
              background:{meta['bg']};
              color:{meta['color']};
              border-radius:6px;
              padding:2px 9px;
              font-size:10px;font-weight:700;
              letter-spacing:0.06em;text-transform:uppercase;
              margin-bottom:7px;
            ">{meta['icon']} {meta['tag']}</div>
            <div style="
              background:#16161e;
              border:1px solid #1e1e28;
              color:#e4e4f0;
              padding:13px 16px;
              border-radius:4px 16px 16px 16px;
              font-size:14px;line-height:1.7;
            ">{content}{sources_html}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:20px 16px 16px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="
          width:36px;height:36px;border-radius:10px;
          background:linear-gradient(135deg,#6366f1,#7c3aed);
          display:flex;align-items:center;justify-content:center;
          font-size:18px;
          box-shadow:0 2px 10px rgba(99,102,241,0.35);
        ">🧠</div>
        <div>
          <div style="font-size:15px;font-weight:700;color:#f0f0f2;letter-spacing:-0.3px;">NeoMind AI</div>
          <div style="font-size:11px;color:#3f3f52;margin-top:1px;">Intelligent Agent v1.0</div>
        </div>
      </div>
    </div>
    <div style="height:1px;background:#1e1e24;margin:0 16px 16px;"></div>
    """, unsafe_allow_html=True)

    # Mode selector
    st.markdown('<div style="font-size:10px;font-weight:700;color:#3f3f52;letter-spacing:0.1em;text-transform:uppercase;padding:0 16px 8px;">Mode</div>', unsafe_allow_html=True)

    for key, meta in MODE_META.items():
        is_active = st.session_state.mode == key
        active_indicator = " ●" if is_active else ""
        label = f"{meta['icon']}  {meta['label']}{active_indicator}"
        if st.button(label, key=f"mode_{key}"):
            st.session_state.mode = key
            st.rerun()

    st.markdown('<div style="height:1px;background:#1e1e24;margin:16px;"></div>', unsafe_allow_html=True)

    # Documents
    st.markdown('<div style="font-size:10px;font-weight:700;color:#3f3f52;letter-spacing:0.1em;text-transform:uppercase;padding:0 16px 8px;">Documents</div>', unsafe_allow_html=True)

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

    if st.session_state.uploaded_docs:
        for doc in st.session_state.uploaded_docs:
            st.markdown(f"""
            <div style="
              background:#16161e;border:1px solid #1e1e28;
              border-radius:8px;padding:7px 12px;margin:4px 16px;
              font-size:12px;color:#6b6b80;
              display:flex;align-items:center;gap:6px;
            ">📄 {doc}</div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
          margin:4px 16px;padding:10px 12px;
          border:1px dashed #1e1e28;border-radius:8px;
          font-size:12px;color:#3f3f52;text-align:center;
        ">No documents uploaded</div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#1e1e24;margin:16px;"></div>', unsafe_allow_html=True)

    # Stats
    st.markdown('<div style="font-size:10px;font-weight:700;color:#3f3f52;letter-spacing:0.1em;text-transform:uppercase;padding:0 16px 8px;">Session</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="
          background:#16161e;border:1px solid #1e1e28;
          border-radius:10px;padding:12px;text-align:center;margin:0 4px 0 16px;
        ">
          <div style="font-size:22px;font-weight:700;color:#f0f0f2;">{len(st.session_state.messages)}</div>
          <div style="font-size:10px;color:#3f3f52;text-transform:uppercase;letter-spacing:0.06em;margin-top:2px;">Msgs</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="
          background:#16161e;border:1px solid #1e1e28;
          border-radius:10px;padding:12px;text-align:center;margin:0 16px 0 4px;
        ">
          <div style="font-size:22px;font-weight:700;color:#f0f0f2;">{len(st.session_state.uploaded_docs)}</div>
          <div style="font-size:10px;color:#3f3f52;text-transform:uppercase;letter-spacing:0.06em;margin-top:2px;">Docs</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑  Clear conversation", key="clear"):
        st.session_state.messages = []
        st.rerun()


# ─── Main ────────────────────────────────────────────────────────────────────
mode = st.session_state.mode
meta = MODE_META[mode]

# Top header bar
st.markdown(f"""
<div style="
  display:flex;align-items:center;justify-content:space-between;
  padding:20px 8px 18px;
  border-bottom:1px solid #1e1e24;
  margin-bottom:4px;
">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="
      width:40px;height:40px;border-radius:12px;
      background:linear-gradient(135deg,#6366f1,#7c3aed);
      display:flex;align-items:center;justify-content:center;
      font-size:20px;
      box-shadow:0 2px 12px rgba(99,102,241,0.3);
    ">{meta['icon']}</div>
    <div>
      <div style="font-size:17px;font-weight:700;color:#f0f0f2;letter-spacing:-0.4px;">
        NeoMind — {meta['label']}
      </div>
      <div style="font-size:12px;color:#3f3f52;margin-top:2px;">{meta['desc']}</div>
    </div>
  </div>
  <div style="
    background:{meta['bg']};color:{meta['color']};
    border-radius:8px;padding:4px 12px;
    font-size:11px;font-weight:700;
    letter-spacing:0.08em;text-transform:uppercase;
  ">{meta['tag']}</div>
</div>
""", unsafe_allow_html=True)

# Chat area
if not st.session_state.messages:
    st.markdown(f"""
    <div style="
      display:flex;flex-direction:column;align-items:center;justify-content:center;
      padding:80px 20px;text-align:center;
    ">
      <div style="
        width:64px;height:64px;border-radius:18px;
        background:linear-gradient(135deg,#6366f1,#7c3aed);
        display:flex;align-items:center;justify-content:center;
        font-size:30px;margin-bottom:20px;
        box-shadow:0 4px 24px rgba(99,102,241,0.3);
      ">🧠</div>
      <div style="font-size:20px;font-weight:700;color:#f0f0f2;letter-spacing:-0.4px;margin-bottom:8px;">
        How can I help you today?
      </div>
      <div style="font-size:14px;color:#3f3f52;max-width:340px;line-height:1.6;">
        Ask me anything — I can chat, search the web, or answer from your documents.
      </div>
      <div style="display:flex;gap:10px;margin-top:28px;flex-wrap:wrap;justify-content:center;">
        <div style="background:#16161e;border:1px solid #1e1e28;border-radius:10px;padding:10px 16px;font-size:13px;color:#6b6b80;">🧠 Explain machine learning</div>
        <div style="background:#16161e;border:1px solid #1e1e28;border-radius:10px;padding:10px 16px;font-size:13px;color:#6b6b80;">🌐 Latest AI news today</div>
        <div style="background:#16161e;border:1px solid #1e1e28;border-radius:10px;padding:10px 16px;font-size:13px;color:#6b6b80;">📄 Summarize my document</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        render_message(msg)

# Input
query = st.chat_input(f"Message NeoMind ({meta['label']})...")

if query:
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "mode": mode,
    })
    with st.spinner(""):
        response_text, sources = placeholder_response(query, mode)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "mode": mode,
        "sources": sources,
    })
    st.rerun()
