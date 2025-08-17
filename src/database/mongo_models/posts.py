from datetime import datetime

from beanie import Document
from pydantic import Field


class Posts(Document):

    title: str
    content: str
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Settings:
        name = "posts"
