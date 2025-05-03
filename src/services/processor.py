from models.document import MarkdownDocument
from models.process_result import ProcessResult
from . import save_embeddings_to_qdrant

class Processor:

    def __init__(self, splitter, embed_client, qdrant):
        self.splitter = splitter
        self.embed_client =embed_client
        self.qdrant = qdrant

    async def run(self, doc: MarkdownDocument):
        chunks = self.splitter.split_to_chunks(doc)
        embeddings = await self.embed_client.embed(chunks)
        await save_embeddings_to_qdrant(self.qdrant, doc.id, chunks, embeddings)
        return ProcessResult("ok", len(chunks), len(embeddings))
