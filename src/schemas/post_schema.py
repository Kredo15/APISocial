from datetime import datetime
from pydantic import BaseModel


class PostAddSchema(BaseModel):
    title: str
    content: str


class PostSchema(PostAddSchema):
    author_id: str
    created_at: datetime
    updated_at: datetime | None = None
