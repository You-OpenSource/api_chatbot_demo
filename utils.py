import json

import requests
import sseclient
import streamlit as st

from prompts import SYSTEM_PROMPT

YDC_API_KEY = st.secrets["YDC_API_KEY"]


def build_prompt():
    prompt = ""
    for msg in st.session_state.messages:
        prompt += msg["role"] + ":\t" + msg["content"] + "\n"
    return prompt


def get_ydc_answer(messages, mode='smart', stream=False):
    query = build_prompt()
    headers = {'x-api-key': YDC_API_KEY}
    endpoint = f"https://chat-api.you.com/{mode}"  # use /research for Research mode
    params = {"query": query, "chat_id": st.session_state.chat_id}
    response = requests.get(endpoint, params=params, headers=headers)
    return response.json()


def get_ydc_stream_answer(mode='smart'):
    query = build_prompt()
    headers = {'x-api-key': YDC_API_KEY}
    endpoint = f"https://chat-api.you.com/{mode}"  # use /research for Research mode
    params = {"query": query, "chat_id": st.session_state.chat_id, "stream": True}
    print(query)
    response = requests.get(endpoint, params=params, headers=headers, stream=True)
    client = sseclient.SSEClient(response)
    full_answer = ''
    for event in client.events():
        print(event)
        if event.event == "token":
            full_answer += event.data
            yield str(event.data)
    print(full_answer)
    return full_answer
