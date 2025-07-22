from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.dependencies import get_current_auth_user
from src.schemas.user import (
    UsersSchema,
    ChangePasswordSchema,
    ResetPasswordSchema
)
from src.services.user import (
    change_password,
    reset_password
)
from src.core.db_dependency import get_async_session
from src.schemas.user import Success

router = APIRouter(prefix='/user', tags=['user'])


@router.patch(
    "/change-password"
)
async def user_change_password(
        user_change_password_body: ChangePasswordSchema,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> Success:
    await change_password(current_user, user_change_password_body, db)
    return Success()


@router.patch("/reset-password")
async def user_reset_password(
        user_reset_password_body: ResetPasswordSchema,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> Success:
    await reset_password(current_user, user_reset_password_body, db)
    return Success()
