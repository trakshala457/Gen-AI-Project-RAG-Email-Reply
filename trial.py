import os
from dotenv import load_dotenv
import streamlit as st

# Local helpers (unchanged):
# - init_gemini() loads GEMINI_API_KEY from .env and configures google-generativeai
# - generate_reply(style_instructions: str, email_text: str) -> str
from gemini_utils import init_gemini, generate_reply
from conversation_manager import init_session

# -----------------------------
# Page config + Minimal CSS for modern chat UI
# -----------------------------
st.set_page_config(page_title="Lexi — AI Email Reply Assistant", page_icon="💬", layout="wide")

# Reduce gap between heading and chat box
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem !important; /* reduce from default ~6rem */
    }
    h1 {
        margin-bottom: 0.5rem !important; /* tighten title spacing */
    }
    </style>
    """,
    unsafe_allow_html=True
)


CUSTOM_CSS = """
<style>
  /* Layout */
  .lexi-app {max-width: 900px; margin: 0 auto;}
  .lexi-header {position: sticky; top: 0; z-index: 5; background: #0f172a; color: #fff; padding: 14px 18px; border-radius: 14px;}
  .lexi-header h1 {font-size: 20px; margin: 0;}
  .lexi-header p {opacity: 0.8; margin: 6px 0 0; font-size: 13px;}

  /* Chat window */
  .lexi-chat {height: calc(100vh - 260px); overflow-y: auto; padding: 18px; background: #0b1020; border-radius: 16px; border: 1px solid #1f2937;}
  .bubble {max-width: 78%; padding: 12px 14px; margin: 10px 0; border-radius: 14px; line-height: 1.45; white-space: pre-wrap;}
  .user   {background: #0ea5e9; color: #001019; border-top-right-radius: 4px;}
  .lexi   {background: #0e1726; color: #e5e7eb; border: 1px solid #1f2a44; border-top-left-radius: 4px;}
  .bubble small {display:block; opacity: 0.8; margin-bottom: 6px; font-weight: 600;}

  /* Sticky composer */
  .composer {position: sticky; bottom: 0; z-index: 10; background: #0b1020; margin-top: 12px; padding: 12px; border: 1px solid #1f2937; border-radius: 16px;}
  .composer h4 {margin: 6px 0 10px; color: #cbd5e1;}
  .composer .hint {opacity: 0.75; font-size: 12px; margin-bottom: 8px;}
  .btn-row {display:flex; gap: 10px; align-items:center;}
  .btn-row button {border-radius: 10px; padding: 8px 12px;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# Init secrets and API
# -----------------------------
load_dotenv()
init_session()  # sets up st.session_state keys used below

try:
    init_gemini()
except Exception as e:
    st.error(f"Gemini init failed: {e}")
    st.stop()

# -----------------------------
# Session vars used by this UI
# -----------------------------
if "stage" not in st.session_state:
    # stages: "input" -> gather style + email, "followup" -> ask for changes or new email
    st.session_state.stage = "input"
if "chat" not in st.session_state:
    # list of dicts: {role: "user"|"lexi", content: str}
    st.session_state.chat = []
if "last_reply" not in st.session_state:
    st.session_state.last_reply = ""

# -----------------------------
# Helpers
# -----------------------------
def push_user(message: str):
    st.session_state.chat.append({"role": "user", "content": message})

def push_lexi(message: str):
    st.session_state.chat.append({"role": "lexi", "content": message})

def generate_first_reply(style: str, email: str) -> str:
    """Use existing generate_reply() to draft the first response."""
    return generate_reply(style, email)

def generate_updated_reply(prev_reply: str, change_request: str) -> str:
    """Ask Gemini to *revise* an existing reply according to change instructions.
    We reuse generate_reply() to avoid new helpers by packing the previous reply
    into the "email_text" field along with clear instructions.
    """
    style_instructions = f"Revise the draft strictly following these changes: {change_request}. Keep formatting email-appropriate."
    email_text = (
        "Previous reply to revise (return only the improved reply):\n" + prev_reply
    )
    return generate_reply(style_instructions, email_text)

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
<div class="lexi-app">
  <div class="lexi-header">
    <h1>Lexi — AI Email Reply Assistant</h1>
    <p>Paste an email, tell Lexi the style, and get a polished reply. Then iterate with change requests.</p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Chat history
# -----------------------------
st.markdown('<div class="lexi-app">', unsafe_allow_html=True)
st.markdown('<div class="lexi-chat">', unsafe_allow_html=True)
for m in st.session_state.chat:
    who = "You" if m["role"] == "user" else "Lexi"
    css = "user" if m["role"] == "user" else "lexi"
    st.markdown(
        f"<div class='bubble {css}'><small>{who}</small>{m['content']}</div>",
        unsafe_allow_html=True,
    )
st.markdown('</div>', unsafe_allow_html=True)  # end chat

# -----------------------------
# Composer (sticky input)
# -----------------------------
st.markdown('<div class="composer">', unsafe_allow_html=True)

if st.session_state.stage == "input":
    st.markdown("### Start a new reply")
    st.markdown(
        "<div class='hint'>Step 1 — Tell Lexi the desired tone & constraints. Step 2 — Paste the incoming email.</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        style = st.text_area(
            "How should the reply be?",
            height=120,
            placeholder="e.g., Formal, concise, acknowledge delay, propose times, add thanks",
            key="style_box",
        )
    with col2:
        email = st.text_area(
            "Email received",
            height=120,
            placeholder="Paste the email content here…",
            key="email_box",
        )

    send = st.button("✨ Generate with Lexi", use_container_width=True)

    if send:
        if not style.strip() or not email.strip():
            st.warning("Please fill both boxes (style and email).")
        else:
            # Push user's inputs as one combined message for readability
            combined = f"**Style**\n{style}\n\n**Email**\n{email}"
            push_user(combined)
            with st.spinner("Lexi is drafting your reply…"):
                try:
                    first = generate_first_reply(style, email)
                    st.session_state.last_reply = first
                    push_lexi(first)
                    st.session_state.stage = "followup"
                except Exception as e:
                    st.error(f"Generation failed: {e}")
            st.rerun()

elif st.session_state.stage == "followup":
    st.markdown("### What next?")
    choice = st.radio(
        "Choose an action:",
        ["Make changes to this reply", "Reply to another email"],
        horizontal=True,
    )

    if choice == "Make changes to this reply":
        changes = st.text_area(
            "Change request",
            height=100,
            placeholder="e.g., Make it warmer, add a line confirming availability, shorten to 4 sentences",
            key="changes_box",
        )
        btns = st.columns([3, 1])
        if btns[0].button("🔁 Update reply with changes", use_container_width=True):
            if not changes.strip():
                st.warning("Please describe the changes you want.")
            else:
                push_user(f"**Change request**\n{changes}")
                with st.spinner("Lexi is updating the reply…"):
                    try:
                        updated = generate_updated_reply(st.session_state.last_reply, changes)
                        st.session_state.last_reply = updated
                        push_lexi(updated)
                    except Exception as e:
                        st.error(f"Update failed: {e}")
                st.rerun()

        if btns[1].button("🗂 New email", use_container_width=True):
            st.session_state.stage = "input"
            st.rerun()

    else:  # Reply to another email
        st.session_state.stage = "input"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # end composer
st.markdown('</div>', unsafe_allow_html=True)  # end app wrapper

# -----------------------------
# Footer note
# -----------------------------
st.caption("Lexi tip: keep style instructions short and concrete — e.g., 'polite, 4 sentences, confirm receipt, propose 2 time slots.'")
