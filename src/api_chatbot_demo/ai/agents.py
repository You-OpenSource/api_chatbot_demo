import secrets

from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.llms import OpenAI
from langchain_community.tools.you import YouSearchTool
from langchain_community.utilities.you import YouSearchAPIWrapper
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint import MemorySaver
from langgraph.prebuilt import chat_agent_executor

from api_chatbot_demo.ai.dataloaders import MultiTypeDataLoader
from api_chatbot_demo.streamlit.utils import UploadedFile


def get_python_agent():
    return create_python_agent(
        llm=OpenAI(temperature=0, max_tokens=1000),
        tool=PythonREPLTool(),
        verbose=True
    )


class ChatBot():
    def run(self, input: str) -> str:
        raise NotImplemented

    def get_chat_history(self) -> ChatMessageHistory:
        raise NotImplemented


class QA_Bot(ChatBot):
    def __init__(
        self,
        llm: ChatOpenAI,
        system_prompt: str,
        files: dict[str, UploadedFile],
        dataloader: MultiTypeDataLoader,
        num_web_results_to_fetch: int = 10
    ):

        self.llm = llm
        self.dataloader = dataloader
        self.system_prompt = prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self.tools = []
        self.agent_memory = MemorySaver()
        self.chat_history = ChatMessageHistory()

        if len(files):
            docs = self.load_files(files)

            files_description = {}
            for _, file in files.items():
                files_description[file.name] = file.description

            # split the docs into chunks, vectorize the chunks and load them into a vector store
            db = self.create_vector_store(docs)

            # convert this retriever into a Langchain tool
            faiss_retriever_tool = create_retriever_tool(
                db.as_retriever(),
                name="file_database",
                description=f"Files in store:\n{str(files_description)}"
            )
            self.tools.append(faiss_retriever_tool)

        # instantiate the YDC search tool in Langchain
        ydc_api_wrapper = YouSearchAPIWrapper(num_web_results=num_web_results_to_fetch)
        ydc_search_tool = YouSearchTool(api_wrapper=ydc_api_wrapper)

        # create a list of tools that will be supplied to the Langchain agent
        self.tools.append(ydc_search_tool)

        agent = create_tool_calling_agent(self.llm, self.tools, self.system_prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True, checkpointer=self.agent_memory)

        # create the agent executor
        # self.agent_executor = chat_agent_executor.create_tool_calling_executor(
        #     self.llm, self.tools, prompt=self.system_prompt, checkpointer=self.agent_memory)

        # generate a thread ID for to keep track of conversation history
        self.thread_id = self.generate_thread_id()

    def load_files(self, files: set[UploadedFile]) -> list:
        docs = []
        for _, file in files.items():
            docs.extend(self.dataloader(file.path))
        return docs

    def create_vector_store(self, docs: list) -> FAISS:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunked_docs = text_splitter.split_documents(docs)
        embeddings = OpenAIEmbeddings()
        return FAISS.from_documents(documents=chunked_docs, embedding=embeddings)

    def generate_thread_id(self) -> str:
        thread_id = secrets.token_urlsafe(16)
        return thread_id

    def run(self, input_str: str) -> str:
        input = {"input": input_str}
        config = {"configurable": {"thread_id": self.thread_id}}

        self.chat_history.add_user_message(input_str)
        output = self.agent_executor.invoke(input=input, config=config)["output"]
        self.chat_history.add_ai_message(output)
        return output

    def get_chat_history(self) -> ChatMessageHistory:
        return self.chat_history
