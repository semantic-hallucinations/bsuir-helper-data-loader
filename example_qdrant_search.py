import requests
from qdrant_client import QdrantClient

# URLs must be localhost:PORT where PORT is an external port from your Docker compose
EMBEDDER_URL = "http://localhost:8081"
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = "test2_documents"


query = "Самодумкин Сергей Александрович"
chunks = []
chunks.append(query)
resp_embeds = requests.post(url=f"{EMBEDDER_URL}/embed", json={"chunks": chunks}).json()
query_embed = resp_embeds["embeddings"][0]

client = QdrantClient(url=QDRANT_URL)
search_result = client.query_points(
    collection_name=QDRANT_COLLECTION_NAME, query=query_embed, limit=10
)
for point in search_result.points:
    print(
        f"Point#{point.id} | Score: {point.score} | Source: {point.payload['source_url']} | Text: {point.payload['content']}"
    )
    print("______________________________________")
