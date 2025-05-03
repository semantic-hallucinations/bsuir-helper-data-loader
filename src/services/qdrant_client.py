from fastapi import Depends, FastAPI
from qdrant_client import models
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from typing import List


async def save_embeddings_to_qdrant(
        qdrant: AsyncQdrantClient,
        doc_id: int,
        chunks: List[str],
        embeddings: List[List[float]],
        collection_name: str = "documents",
        batch_size: int = 64
) -> None:
    points: List[models.PointStruct] = []
    for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        point = models.PointStruct(
            id = f"{doc_id}_{idx}",
            vector=vector,
            payload={
                "doc_id": doc_id,
                "text": chunk
            }
        )
        points.append(point)
    
    for i in range(0, len(points), batch_size):
        await qdrant.upsert(
            collection_name=collection_name,
            points=points[i : i + batch_size]
        )


def get_qdrant_client(app: FastAPI = Depends()) -> AsyncQdrantClient:
    return app.state.qdrant