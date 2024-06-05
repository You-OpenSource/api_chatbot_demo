import os
from typing import Callable

import dotenv
import streamlit as st
from langchain.chains import ConversationChain

from api_chatbot_demo.ai.chains import get_basic_conversation_chain
from api_chatbot_demo.streamlit.llm_blocks import llm_chatbot_st_block

dotenv.load_dotenv(".env", override=True)


@st.cache_resource
def get_chatbot_resource() -> ConversationChain:
    return get_basic_conversation_chain(model_name='gpt-3.5-turbo')


st.set_page_config(page_title="Chatbot Demo", page_icon="🤖")

st.info(
    '''This page demos a simple Chatbot. 
Chat with it and watch it keep track of the conversation.''',
    icon="ℹ️"
)


#### File Upload Section ####

# Initialize a session state to keep track of uploaded files
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

st.title("File Upload Example")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "csv", "db"])

if uploaded_file is not None:
    # Save the uploaded file to the session state
    st.session_state.uploaded_files.append(uploaded_file.name)
    # Save the file to an 'uploads' directory
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    with open(os.path.join('uploads', uploaded_file.name), 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

#### Display Uploaded Files ####
st.header("Uploaded Files")

if st.session_state.uploaded_files:
    for file_name in st.session_state.uploaded_files:
        st.write(file_name)
else:
    st.write("No files uploaded yet!")


# A section where the Create Bot button and empty page logic is added
st.header("Create ChatBot")
create_bot_button = st.button("Create Bot")

if create_bot_button:
    if st.session_state.uploaded_files:
        # If there are uploaded files present, you can instantiate the LLM
        bot_resource = get_chatbot_resource()

        # Redirect or refresh the page to the chat interface after the bot creation
        st.experimental_rerun()
    else:
        st.warning("Please upload at least one file to proceed with bot creation.")

# This condition checks if the bot has been created by verifying resources,
# then initializes the chat interface.
if 'bot_resource' in locals() or 'bot_resources' in globals():
    llm_chatbot_st_block("ChatBot", bot_resource)
else:
    st.empty()


# llm_chatbot_st_block("ChatBot", get_chatbot_resource())
