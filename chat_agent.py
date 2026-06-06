import os
import sqlite3
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

os.environ["GROQ_API_KEY"] = "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"

# 1. Define the State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Initialize LLM and define the Agent Node
llm = ChatGroq(model="llama-3.1-8b-instant")

def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 3. Build the Graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# 4. Set up Persistent Memory (SQLite)
# This creates a local file named 'chat_history.db' in your folder
conn = sqlite3.connect("chat_history.db", check_same_thread=False)
memory = SqliteSaver(conn)

# Compile the graph using our SQLite memory
graph = builder.compile(checkpointer=memory)

# 5. Interactive Chat Loop
def chat():
    print("🤖 Agent started! Type 'quit' to exit.")
    print("💡 Try telling it your name, type 'quit', run the script again, and ask it what your name is!\n")
    
    # The thread_id determines WHICH conversation to load from the database.
    # Hardcoding "user_123" means it will always load this specific chat history.
    config = {"configurable": {"thread_id": "web_user_002"}}

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        # Send the user's message to the graph
        user_message = HumanMessage(content=user_input)
        
        # We use .stream() to get the response back nicely
        events = graph.stream(
            {"messages": [user_message]}, 
            config, 
            stream_mode="values"
        )
        
        # Print the AI's latest response
        for event in events:
            latest_message = event["messages"][-1]
            # Ensure we only print what the AI says, not our own input
            if latest_message.type == "ai":
                print(f"Agent: {latest_message.content}\n")

if __name__ == "__main__":
    chat()