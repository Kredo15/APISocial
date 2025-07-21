from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.auth_service import (
    login_for_access_token,
    register_user
)
from src.database.db import get_async_session
from src.auth.schemas import (
    TokenDataSchema,
    UsersAddSchema,

)

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/sign-in")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    data = await login_for_access_token(form_data, db)
    return data


@router.post("/sign-up")
async def signup(
        user: UsersAddSchema,
        db: AsyncSession = Depends(get_async_session),
) -> TokenDataSchema:
    data = await register_user(user, db)
    return data
