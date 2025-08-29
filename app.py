import streamlit as st
from conversation_manager import init_session, add_message, store_history
from gemini_utils import init_gemini, generate_reply

st.set_page_config(page_title="📧 Lexi — AI Email Reply Assistant", layout="wide")
st.title("🤖 Meet Lexi — Your AI Email Reply Assistant")

init_session()
try:
    init_gemini()
except ValueError as e:
    st.error(str(e))
    st.stop()

#**init_session**>>>Initializes conversation state and Gemini API.
# Stops app if no API key.validate the environment setup early 
# — if the API key is missing, I stop the app immediately to prevent confusing errors later.

#New Email Mode >>> Displays two text areas for style + email.
# If both filled, calls generate_reply and saves results.
if st.session_state.conversation_mode == "new_email":
    style_input = st.text_area("✏️ How should the reply be?", placeholder="e.g., Formal and concise, friendly and appreciative...")
    email_input = st.text_area("📩 Paste the email you received here", placeholder="Paste your incoming email here...")

    if st.button("Generate Reply"):
        if not style_input or not email_input:
            st.error("Please fill in both the boxes")
        else:
            reply = generate_reply(style_input, email_input)
            st.session_state.last_reply=reply
            add_message("assistant", reply)
            store_history(email_input, reply)
            st.session_state.conversation_mode = "post_reply"

#Pst Reply Mode >>> Shows reply, then gives user choice on what’s next.
elif st.session_state.conversation_mode == "post_reply":
    st.subheader("✉️ Drafted Reply:")
    st.markdown(st.session_state.last_reply)

choice = st.radio("What do you want to do next?", ["Request changes", "Reply to another email"])

#Want changes in the answer Email >>> Sends last reply + change request to model for editing.
if choice == "Request changes":
    changes_request = st.text_area("🔄 What changes should I make to the reply?")
    if st.button("Update Reply"):
        updated_reply = generate_reply(changes_request, st.session_state.last_reply)
        st.session_state.last_reply = updated_reply
        add_message("assistant", updated_reply)
        store_history(changes_request, updated_reply)
        st.session_state.conversation_mode = "post_reply"

with st.expander("💬 Conversation History"):
    for msg in st.session_state.messages:
        role = "🧑‍💼 You" if msg["role"] == "user" else "🤖 Lexi"
        st.write(f"**{role}:** {msg['content']}")