import secrets

from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from langchain.memory import ChatMessageHistory
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.tools.you import YouSearchTool
from langchain_community.utilities.you import YouSearchAPIWrapper
from langchain_community.vectorstores import FAISS
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
        files: set[UploadedFile],
        dataloader: MultiTypeDataLoader,
        num_web_results_to_fetch: int = 10
    ):

        self._llm = llm
        self.dataloader = dataloader

        docs = self._load_files(files)

        # split the docs into chunks, vectorize the chunks and load them into a vector store
        db = self._create_vector_store(docs)

        # create a retriever from the vector store
        self._faiss_retriever = db.as_retriever()

        # convert this retriever into a Langchain tool
        self._faiss_retriever_tool = create_retriever_tool(
            self._faiss_retriever,
            name="law_dataset_retriever",
            description="Retrieve relevant context from the US laws dataset."
        )

        # instantiate the YDC search tool in Langchain
        self._ydc_api_wrapper = YouSearchAPIWrapper(num_web_results=num_web_results_to_fetch)
        self._ydc_search_tool = YouSearchTool(api_wrapper=self._ydc_api_wrapper)

        # create a list of tools that will be supplied to the Langchain agent
        self._tools = [self._faiss_retriever_tool, self._ydc_search_tool]

        # Create a checkpointer to use memory
        self._memory = MemorySaver()
        self.chat_history = ChatMessageHistory()

        # create the agent executor
        self._agent_executor = chat_agent_executor.create_tool_calling_executor(
            self._llm, self._tools, checkpointer=self._memory)

        # self._agent_executor = chat_agent_executor.create_tool_calling_executor(
        #     self._llm, self._tools)

        # generate a thread ID for to keep track of conversation history
        self._thread_id = self._generate_thread_id()

    def _load_files(self, files: set[UploadedFile]) -> list:
        docs = []
        for file in files:
            docs.extend(self.dataloader(file.path))
        return docs

    def _create_vector_store(self, docs: list) -> FAISS:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunked_docs = text_splitter.split_documents(docs)
        embeddings = OpenAIEmbeddings()
        return FAISS.from_documents(documents=chunked_docs, embedding=embeddings)

    def _generate_thread_id(self) -> str:
        thread_id = secrets.token_urlsafe(16)
        return thread_id

    def run(self, input_str: str) -> str:
        input = {"messages": input_str}
        config = {"configurable": {"thread_id": self._thread_id}}

        self.chat_history.add_user_message(input_str)
        output = self._agent_executor.invoke(input=input, config=config)["messages"][-1].content
        self.chat_history.add_ai_message(output)
        return output

    def get_chat_history(self) -> ChatMessageHistory:
        return self.chat_history
