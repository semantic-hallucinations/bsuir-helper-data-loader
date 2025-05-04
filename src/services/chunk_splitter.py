from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from langchain.text_splitter import MarkdownTextSplitter

from models import BaseDocument, MarkdownDocument

D = TypeVar("D", bound=BaseDocument)


class BaseChunkSplitter(ABC, Generic[D]):

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def split_to_chunks(self, document: D) -> List[str]: ...


class MarkdownChunkSplitter(BaseChunkSplitter[MarkdownDocument]):

    def __init__(self, chunk_size=800, chunk_overlap=100):
        super().__init__(chunk_size, chunk_overlap)
        self._splitter = MarkdownTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split_to_chunks(self, document: MarkdownDocument) -> List[str]:
        return self._splitter.split_text(document.markdown)
