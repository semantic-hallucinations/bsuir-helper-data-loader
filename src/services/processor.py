import logging
import os
from typing import List

from organisation_utils.logging_config import logger_factory

from models.document import MarkdownDocument
from models.process_result import ProcessResult
from services.qdrant_client import save_embeddings_to_qdrant

from .markdown_cleaner import clean_markdown_for_embeddings, clean_markdown_for_saving

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
        logger.log(logging.INFO, "Preproccessing chunks...")
        cleaned_chunks = await clear_small_chunks(chunks)
        cleaned_embed_chunks = await clean_markdown_for_embeddings(cleaned_chunks)
        cleaned_save_chunks = await clean_markdown_for_saving(cleaned_chunks)
        logger.log(logging.INFO, "Getting embeddings...")
        embeddings = await self.embed_client.embed(cleaned_embed_chunks)
        # logger.log(logging.INFO, str(cleaned_chunks))
        logger.log(logging.INFO, "Embeddings received")

        logger.log(logging.INFO, "Saving to Qdrant...")
        await save_embeddings_to_qdrant(
            self.qdrant,
            doc,
            cleaned_save_chunks,
            embeddings,
            os.getenv("QDRANT_COLLECTION_NAME", None),
        )
        return ProcessResult(
            status="ok", chunks=len(cleaned_chunks), embeddings=len(embeddings)
        )


async def clear_small_chunks(chunks: List[str]) -> List[str]:
    cleaned_chunks = []
    for chunk in chunks:
        if len(chunk.split()) >= 2:
            cleaned_chunks.append(chunk)
    return cleaned_chunks
