from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth import (
    login_for_access_token,
    register_user,
    confirm_user
)
from src.services.auth import refresh_jwt, logout_user
from src.core.db_dependency import get_async_session
from src.schemas.auth import TokenDataSchema, Success
from src.schemas.user import UsersAddSchema, UsersSchema
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
        user: UsersAddSchema,
        db: AsyncSession = Depends(get_async_session),
) -> TokenDataSchema:
    data = await register_user(response, user, db)
    return data


@router.post("/register_confirm")
async def confirm_registration(
        token: str,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
):
    await confirm_user(token, db)
    return {"message": "Электронная почта подтверждена"}


@router.post("/refresh")
async def refresh(
        response: Response,
        refresh_token: str | None = Cookie(default=None),
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    data = await refresh_jwt(refresh_token, response, current_user, db)
    return data


@router.patch("/sign-out")
async def logout(
        request: Request,
        response: Response,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> Success:
    await logout_user(request, response, current_user, db)
    return Success()
