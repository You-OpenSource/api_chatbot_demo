import sys
from contextlib import contextmanager
from time import perf_counter
import json

import requests
import streamlit.components.v1 as components
import streamlit as st
from ansi2html import Ansi2HTMLConverter
import sseclient



class UploadedFile:
    def __init__(self, name, path, description=None):
        self.name = name
        self.path = path
        self.description = description


class TeeStream:
    def __init__(self, original_stream, additional_target):
        self.original_stream = original_stream
        self.additional_target = additional_target

    def write(self, text):
        self.original_stream.write(text)
        self.additional_target.write(text)

    def flush(self):
        self.original_stream.flush()
        self.additional_target.flush()


@contextmanager
def redirect_stdout_copy(new_target):
    tee_stream = TeeStream(sys.stdout, new_target)
    old_target, sys.stdout = sys.stdout, tee_stream  # replace sys.stdout
    try:
        yield tee_stream  # run some code with the replaced stdout
    finally:
        sys.stdout = old_target  # restore to the previous value


@contextmanager
def catchtime() -> float:
    start = perf_counter()
    yield lambda: perf_counter() - start


def render_stdout(std_out: str):
    ansi_converter = Ansi2HTMLConverter()
    html_output = ansi_converter.convert(std_out)
    components.html(html_output, height=600, scrolling=True)


ydc_api_key = st.secrets["YDC_API_KEY"]

def build_prompt():
    prompt = ""
    for msg in st.session_state.messages:
        prompt += msg["role"] + ":\t" + msg["content"] + "\n"
    return prompt


def get_ydc_answer(messages, mode='smart', stream=False):
    query = build_prompt()
    headers = {'x-api-key': ydc_api_key}
    endpoint = f"https://chat-api.you.com/{mode}" # use /research for Research mode
    params = {"query":query, "chat_id": st.session_state.chat_id}
    response = requests.get(endpoint, params=params, headers=headers)
    return response.json()

def get_ydc_stream_answer(mode='smart'):
    query = build_prompt()
    headers = {'x-api-key': ydc_api_key}
    endpoint = f"https://chat-api.you.com/{mode}" # use /research for Research mode
    params = {"query": query, "chat_id": st.session_state.chat_id, "stream": True}
    response = requests.get(endpoint, params=params, headers=headers, stream=True)
    client = sseclient.SSEClient(response)
    full_answer = ''
    for event in client.events():
        if event.event == "token":
            full_answer += event.data
            yield str(event.data)
    return full_answer




