
import io
import os
from itertools import zip_longest

import matplotlib.pyplot as plt
import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from streamlit_chat import message

from api_chatbot_demo.ai.agents import ChatBot
from api_chatbot_demo.streamlit.utils import (
    UploadedFile,
    catchtime,
    redirect_stdout_copy,
    render_stdout,
)


def save_stdout_to_state(name: str, func: callable, *args, **kwargs):
    with st.spinner(f"running {name}..."):
        with catchtime() as t:
            with io.StringIO() as buf, redirect_stdout_copy(buf):
                func(*args, **kwargs)
                st.session_state[name] = buf.getvalue()
        if t() > 0.05:
            print(f"{name} took {t():.2f}s")


def build_message_list():
    """
    Build a list of messages including system, human and AI messages.
    """
    # Start zipped_messages with the SystemMessage
    zipped_messages = [SystemMessage(
        content=st.session_state['prompt']
    )]

    # Zip together the past and generated messages
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(
                content=human_msg))  # Add user messages
        if ai_msg is not None:
            zipped_messages.append(
                AIMessage(content=ai_msg))  # Add AI messages

    return zipped_messages


def generate_response(chatbot: ConversationChain):
    """
    Generate AI response using the ChatOpenAI model.
    """
    # Build the list of messages
    zipped_messages = build_message_list()

    # Generate response using the chat model
    with st.status("Thinking..."):
        ai_response = chatbot(zipped_messages)

    return ai_response.content


def llm_stdout_st_block(name, func: callable, *args, **kwargs):
    name_var = name.lower().replace(" ", "_")
    std_out_var = f"{name_var}_std_output"
    st.header(f"{name}")
    input_text = st.text_area("Agent Input", key=f"{name_var}_input_text")
    button = st.button(f"Send to {name}", key=f"{name_var}_run_button")
    if button:
        print(f"{name} input:\n{input_text}")
        save_stdout_to_state(std_out_var, func, input_text, *args, **kwargs)
    else:
        pass
    if std_out_var in st.session_state:
        with st.expander(f"{name} Response", expanded=True):
            render_stdout(st.session_state[std_out_var])


def chat_memory_st_block(chat_memory: ChatMessageHistory):
    for i, _message in enumerate(chat_memory.messages):
        if isinstance(_message, HumanMessage):
            # message(_message.content, is_user=True, key=str(i) + "_user")
            with st.chat_message("user"):
                st.markdown(_message.content)

        elif isinstance(_message, AIMessage):
            # message(_message.content, key=str(i))
            with st.chat_message("assistant"):
                st.markdown(_message.content)


def llm_conversation_chain_st_block(name, chatbot: ConversationChain):
    st.header(f"{name}")

    if user_input := st.chat_input("Send to chatbot"):
        print(f"{name} input:\n{user_input}")
        output = chatbot.run(user_input)
        print(f"{name} output:\n{output}")

    if len(chatbot.memory.chat_memory.messages) > 0:
        with st.expander(f"{name} Response", expanded=True):
            chat_memory_st_block(chatbot.memory.chat_memory)


def llm_chatbot_st_block(name, chatbot: ChatBot):
    st.header(f"{name}")

    if user_input := st.chat_input("Send to chatbot"):
        print(f"{name} input:\n{user_input}")
        output = chatbot.run(user_input)
        print(f"{name} output:\n{output}")

    chat_history = chatbot.get_chat_history()
    if len(chat_history.messages) > 0:
        with st.expander(f"{name} Response", expanded=True):
            chat_memory_st_block(chat_history)


def llm_system_prompt_block():
    st.header(f"System Prompt")

    # Check if 'system_prompt' is already in session_state, if not, initialize an empty string
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = "You are a helpful assistant."

    # Text input for user to define a system prompt
    user_defined_prompt = st.text_area(
        "Define a system prompt",
        height=150,
        value=st.session_state.system_prompt
    )

    # When the user updates the prompt, save it into the session state
    if user_defined_prompt:
        st.session_state.system_prompt = user_defined_prompt


def file_upload_st_block():
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}

    st.header("File Upload Example")

    description = st.text_input("File Description", key=f"uploaded_file_description")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "csv", "db"])
    if uploaded_file is not None and description is not None:
        if uploaded_file.name in st.session_state.uploaded_files:
            st.warning(f"File with name {uploaded_file.name} already uploaded. Replacing")

        if not os.path.exists('.uploads'):
            os.makedirs('.uploads')
        filepath = os.path.join('.uploads', uploaded_file.name)

        # Save the uploaded file to the session state
        st.session_state.uploaded_files[uploaded_file.name] = UploadedFile(
            name=uploaded_file.name, path=filepath, description=description
        )

        # Save the file to an 'uploads' directory
        with open(filepath, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Display Uploaded Files
    st.header("Uploaded Files")
    if st.session_state.uploaded_files:
        for name, file in st.session_state.uploaded_files.items():
            st.write(f"{name}: {file.description}")
    else:
        st.write("No files uploaded yet!")


def plot_temp_chart():
    if os.path.isfile('temp_chart.png'):
        im = plt.imread('temp_chart.png')
        st.image(im)
        os.remove('temp_chart.png')
