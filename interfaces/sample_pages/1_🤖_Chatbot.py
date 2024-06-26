from typing import Callable

import dotenv
import streamlit as st
from langchain.chains import ConversationChain

from api_chatbot_demo.ai.chains import get_basic_conversation_chain
from api_chatbot_demo.streamlit.llm_blocks import llm_conversation_chain_st_block

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
llm_conversation_chain_st_block("ChatBot", get_chatbot_resource())
