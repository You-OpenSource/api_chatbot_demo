import os
import time

import dotenv
import streamlit as st
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI

from api_chatbot_demo.ai.agents import QA_Bot
from api_chatbot_demo.ai.chains import get_basic_conversation_chain
from api_chatbot_demo.ai.dataloaders import MultiTypeDataLoader
from api_chatbot_demo.streamlit.llm_blocks import (
    file_upload_st_block,
    llm_chatbot_st_block,
    llm_system_prompt_block,
)

dotenv.load_dotenv(".env", override=True)


@st.cache_resource
def get_chatbot_resource() -> ConversationChain:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    return QA_Bot(
        llm,
        files=st.session_state.uploaded_files,
        system_prompt=st.session_state.system_prompt,
        dataloader=MultiTypeDataLoader(),
        num_web_results_to_fetch=10
    )


st.set_page_config(page_title="Chatbot Demo", page_icon="🤖")

# Define different stages of the app
CONFIGURATION_STAGE = 'configuration_stage'
BOT_STAGE = 'bot_stage'

if 'current_stage' not in st.session_state:
    st.session_state.current_stage = CONFIGURATION_STAGE


def enter_bot_stage():
    """Switch to the bot stage and rerun the app."""
    st.session_state.current_stage = BOT_STAGE
    # Instantiate the LLM
    st.session_state.chatbot_resource = get_chatbot_resource()
    st.rerun()


def enter_configuration_stage():
    """Switch to the configuration stage and rerun the app."""
    st.session_state.current_stage = CONFIGURATION_STAGE
    # Instantiate the LLM
    st.rerun()


st.info(
    '''This page demos a simple Chatbot.
    Chat with it and watch it keep track of the conversation.''',
    icon="ℹ️"
)

# Configuration Stage: File Upload and Create Bot Button
if st.session_state.current_stage == CONFIGURATION_STAGE:
    llm_system_prompt_block()
    file_upload_st_block()

    create_bot_button = st.button("Create Bot")

    if create_bot_button:
        enter_bot_stage()

# Bot Stage: Chat Interface
if st.session_state.current_stage == BOT_STAGE:
    configure_bot_button = st.button("Configure Bot")

    if configure_bot_button:
        enter_configuration_stage()
    # Ensure we have a chatbot resource before rendering the chat interface
    if st.session_state.chatbot_resource:
        llm_chatbot_st_block("ChatBot", st.session_state.chatbot_resource)
    else:
        # If somehow reached here without a chatbot resource, prompt back to configuration stage
        st.error("An error occurred. Please go back to upload files.")
