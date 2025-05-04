from pydantic import BaseModel


class BaseDocument(BaseModel):
    pass


class MarkdownDocument(BaseDocument):
    source_url: str
    content: str
