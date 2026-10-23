import streamlit as st
from google import genai
from google.genai import types
import firebase_admin
from firebase_admin import credentials, firestore
import json
import uuid

st.set_page_config(
    page_title="Nguyễn Minh Huy 💕 Tô Nguyễn Thanh Quyên",
    page_icon="💖",
    layout="centered"
)

if not firebase_admin._apps:
    try:
        raw_key = st.secrets["FIREBASE_KEY"]
        if isinstance(raw_key, str):
            key_dict = json.loads(raw_key.strip(), strict=False)
        else:
            key_dict = dict(raw_key)

        if "private_key" in key_dict:
            key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Lỗi khởi tạo Firebase: {e}")
        st.stop()

db = firestore.client()
chats_ref = db.collection("chats")
messages_ref = db.collection("chat_messages")

st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        background-image: url("https://i.pinimg.com/736x/80/c8/10/80c810d7a9426f316bf49842f1b80bf8.jpg");
        background-repeat: repeat;
        background-size: 300px;
    }
    .stChatMessage {
        background-color: transparent !important;
        padding: 6px 10px !important;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="chat avatar 👧"]),
    div[data-testid="stChatMessage"]:has(div:contains("user")) {
        flex-direction: row-reverse !important;
        text-align: right !important;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="chat avatar 👧"]) .stMarkdown,
    div[data-testid="stChatMessage"]:has(div:contains("user")) .stMarkdown {
        background: linear-gradient(135deg, #8A2BE2, #6A0DAD) !important;
        color: #FFFFFF !important;
        border-radius: 18px 18px 2px 18px !important;
        padding: 10px 16px !important;
        display: inline-block !important;
        max-width: 80% !important;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="chat avatar 🐰"]),
    div[data-testid="stChatMessage"]:has(div:contains("assistant")) {
        flex-direction: row !important;
        text-align: left !important;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="chat avatar 🐰"]) .stMarkdown,
    div[data-testid="stChatMessage"]:has(div:contains("assistant")) .stMarkdown {
        background-color: #262626 !important;
        color: #F0F0F0 !important;
        border-radius: 18px 18px 18px 2px !important;
        padding: 10px 16px !important;
        display: inline-block !important;
        max-width: 80% !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💕💘 Trò Chuyện Cùng Chồng Iu (Bin - Thỏ)")

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)

    system_instruction = "Bạn là trợ lý ảo thân thiện."

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        role_icon = "👧" if message["role"] == "user" else "🐰"
        with st.chat_message(message["role"], avatar=role_icon):
            st.markdown(message["content"])

    if prompt := st.chat_input("Nhắn lời yêu thương..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👧"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🐰"):
            contents = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            reply_text = response.text
            st.markdown(reply_text)
            st.session_state.messages.append({"role": "assistant", "content": reply_text})

except Exception as e:
    st.error(f"Có lỗi xảy ra: {e}")
