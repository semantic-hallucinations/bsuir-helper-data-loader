import uuid
from typing import List

from fastapi import Request
from qdrant_client import models
from qdrant_client.async_qdrant_client import AsyncQdrantClient

from models import MarkdownDocument


async def save_embeddings_to_qdrant(
    qdrant: AsyncQdrantClient,
    doc: MarkdownDocument,
    chunks: List[str],
    embeddings: List[List[float]],
    collection_name: str = "documents",
    batch_size: int = 64,
) -> None:
    points: List[models.PointStruct] = []
    for chunk, vector in zip(chunks, embeddings):
        point = models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"source_url": doc.source_url, "content": chunk},
        )
        points.append(point)

    for i in range(0, len(points), batch_size):
        await qdrant.upsert(
            collection_name=collection_name, points=points[i : i + batch_size]
        )


def get_qdrant_client(request: Request) -> AsyncQdrantClient:
    return request.app.state.qdrant
