from pydantic import BaseModel


class BaseDocument(BaseModel):
    id: int


class MarkdownDocument(BaseDocument):
    markdown: str
