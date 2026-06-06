import os
import sqlite3
import PyPDF2
import streamlit as st
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage


from langchain_groq import ChatGroq
os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(model="llama-3.1-8b-instant")

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build Graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# Persistent Memory Connection
conn = sqlite3.connect("chat_history.db", check_same_thread=False)
memory = SqliteSaver(conn)
graph = builder.compile(checkpointer=memory)

# =========================================================
# 3. STREAMLIT WEB UI (Clean Screen, Hidden Memory)
# =========================================================
st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖", layout="wide")

# --- SIDEBAR: DOCUMENT UPLOAD ---
with st.sidebar:
    st.header("📄 Document Analysis")
    uploaded_file = st.file_uploader("Upload a PDF to analyze", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Analyze & Summarize"):
            with st.spinner("Reading PDF..."):
                # 1. Extract text
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                extracted_text = ""
                for page in pdf_reader.pages:
                    # Some pages return None, so we handle that safely
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
                
                # 2. THE SAFETY NET: Check if extraction worked
                if not extracted_text.strip():
                    st.error("🚨 Error: Could not read text from this PDF. It might be a scanned image, a protected file, or completely empty.")
                else:
                    # ==========================================
                    # NEW FIX: TRUNCATE TEXT TO SURVIVE RATE LIMITS
                    # ==========================================
                    # 1 token is ~4 characters. Limiting to 15,000 characters (~3,750 tokens)
                    # leaves plenty of room for the chat history and the AI's response.
                    safe_text = extracted_text[:8000]
                    
                    if len(extracted_text) > 8000:
                        st.warning("⚠️ Document is very large! Analyzing the first section to stay within free tier limits.")
                    
                    # 3. Format the prompt using our newly sliced safe_text
                    summary_prompt = f"""
                    I have uploaded a document named '{uploaded_file.name}'. 
                    Please thoroughly analyze the following text and provide a comprehensive summary:
                    
                    --- DOCUMENT TEXT START ---
                    {safe_text}
                    --- DOCUMENT TEXT END ---
                    """
                    
                    st.session_state.ui_messages.append({"role": "user", "content": f"📁 *Uploaded {uploaded_file.name} for analysis.*"})
                    
                    config = {"configurable": {"thread_id": "web_user_001"}}
                    input_message = HumanMessage(content=summary_prompt)
                    response_state = graph.invoke({"messages": [input_message]}, config)
                    
                    ai_response = response_state["messages"][-1].content
                    st.session_state.ui_messages.append({"role": "assistant", "content": ai_response})
                    
                    st.success("Analysis Complete!")
                    
# --- MAIN CHAT WINDOW ---
st.title("🤖 My Persistent AI Assistant")
st.caption("Powered by LangGraph, SQLite Memory, and Streamlit")

config = {"configurable": {"thread_id": "web_user_002"}}

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []

# Render past messages
for msg in st.session_state.ui_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Standard Chat Input
if user_query := st.chat_input("Type your message or ask questions about the PDF..."):
    st.session_state.ui_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            input_message = HumanMessage(content=user_query)
            response_state = graph.invoke({"messages": [input_message]}, config)
            
            ai_response = response_state["messages"][-1].content
            st.write(ai_response)
            st.session_state.ui_messages.append({"role": "assistant", "content": ai_response})