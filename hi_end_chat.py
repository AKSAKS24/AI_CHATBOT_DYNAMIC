import streamlit as st
import json
import requests
from frontend.ui.components import show_message, typing_effect

# ---------- Configuration ----------
st.set_page_config(page_title="SAP AI Chatbot", page_icon="🤖", layout="wide")

with open("frontend/ui/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

AI_AVATAR = "frontend/assets/ai_avatar.png"
USER_AVATAR = "frontend/assets/user_avatar.png"
BASE_URL = "http://localhost:8080/odata/fetch"   # FastAPI backend

# ---------- Session State ----------
for key in ["chat", "step", "service", "entity", "fields", "filters"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "chat" else None

# ---------- Load Config ------------
def load_config():
    with open("config/odata_endpoints.json") as f:
        return json.load(f)

odata_cfg = load_config()

# ---------- Greeting ---------------
if not st.session_state.step:
    st.session_state.step = "service"
    typing_effect(
        "assistant",
        "👋 Hello! I'm your SAP OData assistant.\nLet's begin — which *Service* would you like to use today?",
        AI_AVATAR
    )

# ---------- Display History --------
for msg in st.session_state.chat:
    show_message(**msg)

# ---------- Chat Input -------------
user_input = st.chat_input("Type your reply...")

if user_input:
    st.session_state.chat.append(
        {"role": "user", "message": user_input, "avatar_path": USER_AVATAR}
    )
    show_message("user", user_input, USER_AVATAR)

    current = st.session_state.step

    # STEP 1 - Service
    if current == "service":
        services = list(odata_cfg["Services"].keys())
        if user_input not in services:
            typing_effect("assistant",
                          f"Please choose one of: {', '.join(services)}",
                          AI_AVATAR)
        else:
            st.session_state.service = user_input
            st.session_state.step = "entity"
            typing_effect("assistant",
                          f"✅ Great! Now pick an *Entity* under **{user_input}**.",
                          AI_AVATAR)

    # STEP 2 - Entity
    elif current == "entity":
        entities = list(
            odata_cfg["Services"][st.session_state.service]["Entities"].keys()
        )
        if user_input not in entities:
            typing_effect("assistant",
                          f"Please choose one of these entities: {', '.join(entities)}",
                          AI_AVATAR)
        else:
            st.session_state.entity = user_input
            st.session_state.step = "fields"
            typing_effect("assistant",
                          f"👌 Nice! Which *fields* would you like? (comma separated)",
                          AI_AVATAR)

    # STEP 3 - Fields
    elif current == "fields":
        possible_fields = odata_cfg["Services"][st.session_state.service]["Entities"][st.session_state.entity]["Fields"]
        selected_fields = [f.strip() for f in user_input.split(",") if f.strip() in possible_fields]
        if not selected_fields:
            typing_effect("assistant",
                          f"Available fields: {', '.join(possible_fields)}",
                          AI_AVATAR)
        else:
            st.session_state.fields = selected_fields
            st.session_state.step = "filters"
            typing_effect("assistant",
                          "👍 Got it! Any filters? (key=value, key=value) or type **no**",
                          AI_AVATAR)

    # STEP 4 - Filters
    elif current == "filters":
        if user_input.lower() == "no":
            st.session_state.filters = {}
        else:
            filters = {}
            try:
                for pair in user_input.split(","):
                    k, v = pair.split("=")
                    filters[k.strip()] = v.strip()
                st.session_state.filters = filters
            except Exception:
                typing_effect("assistant",
                              "⚠️ Please use the correct format: key=value, key=value",
                              AI_AVATAR)
                st.stop()

        st.session_state.step = "confirm"
        fields = ", ".join(st.session_state.fields)
        summary = (
            f"<b>Confirm:</b><br>"
            f"Service: {st.session_state.service}<br>"
            f"Entity: {st.session_state.entity}<br>"
            f"Fields: {fields}<br>"
            f"Filters: {st.session_state.filters or 'None'}<br>"
            f"Shall I fetch the data now? (yes/no)"
        )
        typing_effect("assistant", summary, AI_AVATAR)

    # STEP 5 - Confirmation
    elif current == "confirm":
        if user_input.lower() in ["yes", "y", "confirm"]:
            with st.spinner("Fetching data from SAP..."):
                payload = {
                    "service_name": st.session_state.service,
                    "entity_name": st.session_state.entity,
                    "fields": st.session_state.fields,
                    "filters": st.session_state.filters,
                }
                try:
                    res = requests.post(BASE_URL, json=payload, timeout=180)
                    if res.status_code == 200:
                        data = res.json()
                        typing_effect("assistant",
                                      "✅ Data successfully retrieved! Here's the result:",
                                      AI_AVATAR)
                        st.json(data)
                        st.balloons()
                    else:
                        typing_effect("assistant",
                                      f"❌ Backend error: {res.text}",
                                      AI_AVATAR)
                except requests.exceptions.RequestException as e:
                    typing_effect("assistant",
                                  f"🚨 Request failed: {e}",
                                  AI_AVATAR)

            # reset for next conversation
            st.session_state.step = "service"
            st.session_state.service = None
            st.session_state.entity = None
            st.session_state.fields = None
            st.session_state.filters = None
            typing_effect("assistant",
                          "Would you like to start another query? Please choose the next *Service*.",
                          AI_AVATAR)
        else:
            typing_effect("assistant", "Cancelled. Choose a new Service to start over 🎯", AI_AVATAR)
            st.session_state.step = "service"