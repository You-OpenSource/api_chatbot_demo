from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader


class MultiTypeDataLoader:
    def __init__(self, handlers: dict[str, callable] = {
        '.pdf': PyPDFLoader,
        '.csv': CSVLoader
    }):
        self.handlers = handlers

    def __call__(self, file: str):
        file_path = Path(file)
        handler = self.handlers.get(file_path.suffix)
        if handler:
            return handler(file_path).load()
        else:
            raise TypeError(f"No handler found for {file_path.suffix} files")
