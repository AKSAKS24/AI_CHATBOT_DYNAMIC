import streamlit as st
import time

def show_message(role: str, message: str, avatar_path: str):
    """Render one chat bubble dynamically."""
    # Determine alignment and bubble class
    if role == "user":
        html = f"""
        <div style="display:flex; justify-content:flex-end; align-items:flex-end; margin-bottom:6px;">
            <div class="chat-bubble user">{message}</div>
            <img src="{avatar_path}" class="avatar">
        </div>
        """
    else:  # assistant / bot
        html = f"""
        <div style="display:flex; justify-content:flex-start; align-items:flex-end; margin-bottom:6px;">
            <img src="{avatar_path}" class="avatar">
            <div class="chat-bubble bot">{message}</div>
        </div>
        """

    # 👇 *This* makes Streamlit actually render the HTML
    st.markdown(html, unsafe_allow_html=True)


def typing_effect(role, message, avatar_path, delay: float = 0.02):
    """Simulate typing effect for assistant messages."""
    placeholder = st.empty()
    accumulated = ""
    for ch in message:
        accumulated += ch
        html = f"""
        <div style="display:flex; justify-content:flex-start; align-items:flex-end; margin-bottom:6px;">
            <img src="{avatar_path}" class="avatar">
            <div class="chat-bubble bot">{accumulated}</div>
        </div>
        """
        placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(delay)

    placeholder.empty()
    show_message(role, message, avatar_path)