import streamlit as st
import uuid
from typing import List, Dict, Any
from api_chatbot_demo.ai.prompts import SYSTEM_PROMPT
from api_chatbot_demo.streamlit.utils import get_ydc_stream_answer


### Better way to clear history
def clear_chat_history():
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state["messages"] = [
            {"role":"system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "What can I help you build today?"}
        ]


with st.sidebar:
    model_select = st.selectbox("Select a model", ["smart", "research"])
    st.button('Reset Chat', on_click=clear_chat_history)


ydc_api_key = st.secrets["YDC_API_KEY"]

st.title("💬 YOU.COM API ASSISTANT")
st.caption("🚀 Let us help you build with You.com")


if "messages" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state["messages"] = [
        {"role":"system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "What can I help you build today?"}
    ]

# Display or clear messages
for msg in st.session_state.messages:
    if msg["role"] != "system":     
        st.chat_message(msg["role"]).write(msg["content"])

# User provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    print(st.session_state.messages)

# Generate response if last reponse not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = get_ydc_stream_answer(model_select)
        full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)