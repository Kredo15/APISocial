from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth_service import (
    login_for_access_token,
    register_user,
    confirm_user
)
from src.services.auth_service import refresh_jwt, logout_user
from src.core.db_dependency import get_async_session
from src.schemas.auth_schema import TokenDataSchema, Success
from src.schemas.user_schema import UserAddSchema, UserSchema
from src.services.dependencies import get_current_auth_user


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/sign-in")
async def login(
        response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    data = await login_for_access_token(response, form_data, db)
    return data


@router.post("/sign-up")
async def signup(
        response: Response,
        user: UserAddSchema,
        db: AsyncSession = Depends(get_async_session),
) -> TokenDataSchema:
    data = await register_user(response, user, db)
    return data


@router.post("/register_confirm/{token}")
async def confirm_registration(
        token: str,
        current_user: UserSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> Success:
    await confirm_user(token, current_user, db)
    return Success()


@router.post("/refresh")
async def refresh(
        response: Response,
        refresh_token: str | None = Cookie(default=None),
        current_user: UserSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    data = await refresh_jwt(refresh_token, response, current_user, db)
    return data


@router.patch("/sign-out")
async def logout(
        request: Request,
        response: Response,
        current_user: UserSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> Success:
    await logout_user(request, response, current_user, db)
    return Success()
