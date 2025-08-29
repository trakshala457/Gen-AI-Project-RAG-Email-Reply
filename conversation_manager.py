import streamlit as st  #Needed for session_state — stores conversation and mode between interactions.
#Streamlit apps are stateless by default, so I use session_state to persist data between UI updates.

def init_session():
    """Initialize conversation state variables."""
    if "conversational_mode" not in st.session_state:
        st.session_state.conversation_mode = "new_email"
    if "last_reply" not in st.session_state:
        st.session_state.last_reply = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if 'history' not in st.session_state:
        st.session_state.history = []
#**init_session()**>>>Ensures all session variables exist before use.
# conversation_mode lets us switch UI between new email and change request.
# set default values in one place to avoid KeyError. This also makes the conversation flow predictable and easy to debug.

def add_message(role, content):
    """Add message to conversation history (for display)."""
    st.session_state.messages.append({"role": role, "content": {content}})
#**add_maessages**>>>Stores chat messages in a structured format for the UI.
# storing messages as dictionaries with a role and content.
# That way I can render them differently for the user and for Lexi.

def store_history(question, answer):
     """Keep only last 5 conversation turns for RAG/context."""
     st.session_state.history.append({"question":{question}, "answer":{answer}})
     if len(st.session_state.history)>5:
         st.session_state.history = st.session_state.history[-5:]
#**store_history**>>>Passing only the last 5 Q&A pairs keeps the context window small,
# which reduces token usage and speeds up responses without losing recent context