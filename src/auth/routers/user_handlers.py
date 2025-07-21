from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.dependencies import get_current_auth_user
from src.auth.services.user_service import (
    refresh_jwt,
    logout_user,
    change_password,
    reset_password
)
from src.database.db import get_async_session
from src.auth.schemas import (
    SuccessOut,
    ChangePasswordSchema,
    ResetPasswordSchema,
    TokenDataSchema,
    UpdateTokensIn,
    UsersSchema
)

router = APIRouter(prefix='/user', tags=['user'])


@router.post("/refresh")
async def refresh(
        token: UpdateTokensIn,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    data = await refresh_jwt(token, current_user, db)
    return data


@router.patch("/sign-out")
async def logout(
        request: Request,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> SuccessOut:
    await logout_user(request, current_user, db)
    return SuccessOut()


@router.patch(
    "/change-password"
)
async def user_change_password(
        user_change_password_body: ChangePasswordSchema,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> SuccessOut:
    await change_password(current_user, user_change_password_body, db)
    return SuccessOut()


@router.patch("/reset-password")
async def user_reset_password(
        user_reset_password_body: ResetPasswordSchema,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> SuccessOut:
    await reset_password(current_user, user_reset_password_body, db)
    return SuccessOut()
