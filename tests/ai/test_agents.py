from typing import Callable


def test_import():
    from api_chatbot_demo.ai.agents import get_python_agent
    assert isinstance(get_python_agent, Callable)
