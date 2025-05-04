from typing import List

from fastapi import Request
from httpx import AsyncClient, HTTPStatusError, TransportError
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)


class EmbedClient:

    def __init__(self, base_url: str, timeout: float = 60.0):
        self._client = AsyncClient(base_url=base_url, timeout=timeout)

    async def close(self):
        await self._client.aclose()

    async def embed(self, chunks: List[str]) -> List[List[float]]:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_fixed(2),
            retry=retry_if_exception_type((TransportError, HTTPStatusError)),
        ):
            with attempt:
                resp = await self._client.post("/embed", json={"chunks": chunks})
                resp.raise_for_status()
                data = resp.json()
                return data["embeddings"]
        raise RuntimeError("Failed to get embeddings after retries")


def get_embed_client(request: Request) -> EmbedClient:
    return request.app.state.embed_client
