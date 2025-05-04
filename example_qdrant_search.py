import os

import requests
from qdrant_client import QdrantClient

EMBEDDER_URL = "http://localhost:8081"
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", None)


query = "выпускник"
chunks = []
chunks.append(query)
resp_embeds = requests.post(url=f"{EMBEDDER_URL}/embed", json={"chunks": chunks}).json()


client = QdrantClient(url=QDRANT_URL)
search_result = client.query_points(
    collection_name=QDRANT_COLLECTION_NAME, query=resp_embeds["embeddings"][0], limit=2
)
for point in search_result.points:
    print(f"Point{point.id} | Score={point.score} | Text: {point.payload['text']}")
    print("______________________________________")
