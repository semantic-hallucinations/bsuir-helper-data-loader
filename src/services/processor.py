import logging
import os
import re
from typing import List

from organisation_utils.logging_config import logger_factory

from models.document import MarkdownDocument
from models.process_result import ProcessResult
from services.qdrant_client import save_embeddings_to_qdrant

logger = logger_factory.get_logger("PROCESSOR LOGGER")


class Processor:

    def __init__(self, splitter, embed_client, qdrant):
        self.splitter = splitter
        self.embed_client = embed_client
        self.qdrant = qdrant

    async def run(self, doc: MarkdownDocument):
        logger.log(logging.INFO, "Splitting chunks...")
        chunks = self.splitter.split_to_chunks(doc)
        logger.log(logging.INFO, "Chunks splitted")

        logger.log(logging.INFO, "Getting embeddings...")
        cleaned_chunks = await self._clean_markdown_chunks(chunks)
        embeddings = await self.embed_client.embed(cleaned_chunks)
        logger.log(logging.INFO, "Embeddings received")

        logger.log(logging.INFO, "Saving to Qdrant...")
        await save_embeddings_to_qdrant(
            self.qdrant,
            doc,
            chunks,
            embeddings,
            os.getenv("QDRANT_COLLECTION_NAME", None),
        )
        return ProcessResult(
            status="ok", chunks=len(chunks), embeddings=len(embeddings)
        )

    async def _clean_markdown_chunks(self, md_chunks: List[str]) -> List[str]:
        cleaned = []
        for chunk in md_chunks.copy():
            text = chunk

            text = re.sub(r"```[\s\S]*?```", "", text)

            text = re.sub(r"`[^`]+`", "", text)

            text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)

            text = re.sub(r"^\s{0,3}[-\*\+]\s+", "", text, flags=re.MULTILINE)

            text = re.sub(r"^\s{0,3}>\s*", "", text, flags=re.MULTILINE)

            text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

            text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)

            text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
            text = re.sub(r"\*(.*?)\*", r"\1", text)
            text = re.sub(r"__(.*?)__", r"\1", text)
            text = re.sub(r"_(.*?)_", r"\1", text)

            text = text.replace("*", "").replace("_", "")

            text = re.sub(r"\s+", " ", text).strip()

            cleaned.append(text)
        return cleaned
