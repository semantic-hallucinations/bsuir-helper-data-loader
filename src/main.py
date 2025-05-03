from fastapi import FastAPI, Depends, HTTPException
import httpx
from models import MarkdownDocument, ProcessResult
from services import (
    MarkdownChunkSplitter,
    EmbedClient,
    get_embed_client,
    get_qdrant_client,
    Processor
)
from contextlib import asynccontextmanager
from qdrant_client import models
from qdrant_client.async_qdrant_client import AsyncQdrantClient


EMBEDDER_URL = "http://localhost:8001"
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = "test_documents"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.embed_client = EmbedClient(base_url=EMBEDDER_URL)
    app.state.qdrant = AsyncQdrantClient(url=QDRANT_URL)

    await app.state.qdrant.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
    )

    yield

    await app.state.embed_client.close()
    await app.state.qdrant.close()


app = FastAPI(lifespan=lifespan)
splitter = MarkdownChunkSplitter(chunk_size=1000, chunk_overlap=100)


@app.get("/health", status_code=200)
def health():
    return {"status": "ok"}


@app.post(
        "/process_markdown/",
        summary="chunk split -> embed -> upsert to Qdrant",
        response_model=ProcessResult
)
async def process_markdown(
    md_doc: MarkdownDocument,
    qdrant: AsyncQdrantClient = Depends(get_qdrant_client),
    embed_client: EmbedClient = Depends(get_embed_client),
):
    proc = Processor(splitter, embed_client, qdrant)
    
    try:
        resp = proc.run(md_doc)
    except httpx.HTTPError:
        raise HTTPException(502, "Embedder failed")
    except Exception:
        raise HTTPException(503, "Qdrant failed")

    return resp
