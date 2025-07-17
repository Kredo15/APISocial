from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.helper import (
    login_for_access_token,
    auth_refresh_jwt,
    register_user,
    logout_user
)
from src.database.db import get_async_session
from src.auth.schemas import (
    TokenDataSchema,
    UsersAddSchema,
    UpdateTokensIn,
    SuccessOut
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/sign-in",
)
router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/sign-in")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    data = await login_for_access_token(form_data, db)
    return data


@router.post(
    "/refresh",
    dependencies=[Depends(oauth2_scheme)]
)
async def refresh(
        token: UpdateTokensIn,
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    data = await auth_refresh_jwt(token, db)
    return data


@router.post("/sign-up")
async def signup(
        user: UsersAddSchema,
        db: AsyncSession = Depends(get_async_session),
) -> TokenDataSchema:
    data = await register_user(user, db)
    return data


@router.post(
    "/logout",
    dependencies=[Depends(oauth2_scheme)]
)
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
) -> SuccessOut:
    await logout_user(request, db)
    return SuccessOut()
