from pydantic import BaseModel


class ProcessResult(BaseModel):
    status: str
    chunks: int
    embeddings: int
