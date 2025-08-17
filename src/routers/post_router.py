from fastapi import APIRouter, Depends

from src.services.dependencies import get_current_auth_user
from src.schemas.post_schema import (
    PostAddSchema,
    PostSchema
)
from src.schemas.user_schema import UserSchema
from src.services.post_service import create_post
router = APIRouter(prefix='/post', tags=['post'])


@router.post("")
async def add_post(
        post: PostAddSchema,
        current_user: UserSchema = Depends(get_current_auth_user)
) -> PostSchema:
    response = await create_post(current_user.uid, post)
    return response
