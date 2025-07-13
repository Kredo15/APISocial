from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.validation import validate_auth_user
from src.database.db import get_async_session
from src.auth.utils import (
    create_tokens,
    get_current_auth_user_for_refresh,
)
from src.auth.crud import create_user, revoke_refresh_token
from src.auth.schemas import TokenDataSchema, UsersAddSchema

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/sign-in/",
)
router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/sign-in", response_model=TokenDataSchema)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    data_user = await validate_auth_user(form_data, db)
    tokens = await create_tokens(data_user, db)
    return tokens


@router.post(
    "/refresh",
    response_model=TokenDataSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(oauth2_scheme)]
)
async def auth_refresh_jwt(
        refresh_token: str,
        request: Request,
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    user_token = await get_current_auth_user_for_refresh(refresh_token, db)
    device_id = request.state.device_id
    tokens = await create_tokens(user_token, db, device_id)
    await revoke_refresh_token(refresh_token, db, device_id)
    return tokens


@router.post("/sign-up")
async def signup(user: UsersAddSchema,
                 db: AsyncSession = Depends(get_async_session),
                 ) -> TokenDataSchema:
    data_user = await create_user(user, db)
    tokens = await create_tokens(data_user, db)
    return tokens
