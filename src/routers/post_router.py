from fastapi import APIRouter, Depends

from src.services.dependencies import get_current_auth_user
from src.schemas.post_schema import (
    PostAddSchema,
    PostSchema,
    PostsSchema
)
from src.schemas.user_schema import UserSchema
from src.services.post_service import (
    create_post,
    get_all_posts
)
router = APIRouter(prefix='/post', tags=['post'])


@router.post("")
async def add_post(
        post: PostAddSchema,
        current_user: UserSchema = Depends(get_current_auth_user)
) -> PostSchema:
    response = await create_post(current_user.uid, post)
    return response


@router.get("/all")
async def get_all(
        current_user: UserSchema = Depends(get_current_auth_user)
):
    response = await get_all_posts()
    return response
