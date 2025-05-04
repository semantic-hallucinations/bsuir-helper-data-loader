import logging
import os

from organisation_utils.logging_config import logger_factory

from models.document import MarkdownDocument
from models.process_result import ProcessResult

from . import save_embeddings_to_qdrant

logger = logger_factory.get_logger("Main logger")


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
        embeddings = await self.embed_client.embed(chunks)
        logger.log(logging.INFO, "Embeddings received")
        logger.log(logging.INFO, "Saving to Qdrant...")
        await save_embeddings_to_qdrant(
            self.qdrant,
            doc.id,
            chunks,
            embeddings,
            os.getenv("QDRANT_COLLECTION_NAME", None),
        )
        return ProcessResult(
            status="ok", chunks=len(chunks), embeddings=len(embeddings)
        )
