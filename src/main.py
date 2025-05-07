import os
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException
from qdrant_client import models
from qdrant_client.async_qdrant_client import AsyncQdrantClient

from models import MarkdownDocument, ProcessResult
from services import (
    EmbedClient,
    MarkdownChunkSplitter,
    Processor,
    get_embed_client,
)
from services.qdrant_client import get_qdrant_client

EMBEDDER_URL = os.getenv("EMBEDDER_URL", None)
QDRANT_URL = os.getenv("QDRANT_URL", None)
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.embed_client = EmbedClient(base_url=EMBEDDER_URL)
    app.state.qdrant = AsyncQdrantClient(url=QDRANT_URL)

    try:
        existing = await app.state.qdrant.get_collections()
        names = [col.name for col in existing.collections]
    except Exception:
        names = []

    if QDRANT_COLLECTION_NAME not in names:
        try:
            await app.state.qdrant.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=1024,
                    distance=models.Distance.COSINE,
                ),
            )
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise

    yield

    await app.state.embed_client.close()
    await app.state.qdrant.close()


app = FastAPI(lifespan=lifespan)
splitter = MarkdownChunkSplitter(chunk_size=1000, chunk_overlap=200)


@app.get("/health", status_code=200)
def health():
    return {"status": "ok"}


@app.post(
    "/process_markdown",
    summary="chunk split -> embed -> upsert to Qdrant",
    response_model=ProcessResult,
)
async def process_markdown(
    md_doc: MarkdownDocument,
    qdrant: AsyncQdrantClient = Depends(get_qdrant_client),
    embed_client: EmbedClient = Depends(get_embed_client),
):
    proc = Processor(splitter, embed_client, qdrant)

    try:
        resp: ProcessResult = await proc.run(md_doc)
    except httpx.HTTPError:
        raise HTTPException(502, "Embedder failed")
    except ... as e:
        raise HTTPException(503, str(e))

    return resp
