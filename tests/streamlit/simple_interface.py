from typing import Callable

import dotenv
import streamlit as st
from langchain.chains import ConversationChain

from api_chatbot_demo.ai.agents import get_python_agent
from api_chatbot_demo.ai.chains import get_basic_conversation_chain
from api_chatbot_demo.streamlit.llm_blocks import (
    llm_conversation_chain_st_block,
    llm_stdout_st_block,
)

dotenv.load_dotenv(".env", override=True)


def get_python_agent_resource() -> Callable:
    return get_python_agent()


def get_chatbot_resource() -> ConversationChain:
    return get_basic_conversation_chain(model_name='gpt-3.5-turbo')


# Streamlit App
st.set_page_config(layout="wide")
st.title('GenAI App Template Interface Example')

# Create to vertical columns for AI and SQL tools
python_col, chatbot_col = st.columns(2)

# Columns Block
with chatbot_col:
    llm_conversation_chain_st_block("ChatBot", get_chatbot_resource())

with python_col:
    def python_agent_run(*args, **kwargs):
        response = get_python_agent_resource().run(*args, **kwargs)
        return response
    llm_stdout_st_block("Python AI Agent", python_agent_run)
