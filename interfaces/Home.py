
import streamlit as st

st.set_page_config(
    page_title="YOU Demo Menu",
    page_icon="🌎",
    layout="wide"
)

st.write("# YOU Interface Demos")

st.markdown(
    """
    ### Welcome to the chatbot [YOU](https://you.com/) demo app. 
    
    Here we provide end-to-end examples of how to build [YOU API](https://api.you.com/) powered chatbotsusing streamlit.
    
    ### Current examples
    
    #### 🤖 Configurable RAG Chatbot
    
    This demo allows you to upload various forms of private data to be used in conjunction with the YOU API to 
    answer user questions. You also have control over the bot system prompt.
    
    #### 📃 YOU API Docs Chatbot
    
    This demo allows you to chat with the [YOU API](https://api.you.com/) documentation, answer questions and even
    write sample code that uses the YOU API.
"""
)
