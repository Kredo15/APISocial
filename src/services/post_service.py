from uuid import UUID
from datetime import datetime

from src.database.mongo_models.posts import Posts
from src.schemas.post_schema import (
    PostAddSchema,
    PostSchema,
    PostsSchema
)


async def create_post(
        user_id: UUID,
        post: PostAddSchema
) -> PostSchema:
    post_dict = post.dict()
    post_dict["author_id"] = str(user_id)
    post_dict["created_at"] = datetime.utcnow()
    new_post = await Posts(**post_dict).create()
    return PostSchema(**new_post.dict(by_alias=True))


async def get_all_posts() -> PostsSchema:
    posts_db = await Posts.find_all().to_list()
    posts = [PostSchema(**post.dict(by_alias=True)) for post in posts_db]
    return PostsSchema(posts=posts)
