from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools.python.tool import PythonREPLTool


def get_python_agent():
    return create_python_agent(
        llm=OpenAI(temperature=0, max_tokens=1000),
        tool=PythonREPLTool(),
        verbose=True
    )
