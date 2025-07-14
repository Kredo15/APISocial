from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import decode_jwt
from src.auth.validation import validate_auth_user
from src.database.db import get_async_session
from src.auth.utils import (
    create_tokens,
    get_current_auth_user_for_refresh,
)
from src.auth.crud import create_user, revoke_refresh_token
from src.auth.schemas import TokenDataSchema, UsersAddSchema, UpdateTokensIn

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/sign-in",
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
    dependencies=[Depends(oauth2_scheme)]
)
async def auth_refresh_jwt(
        token: UpdateTokensIn,
        db: AsyncSession = Depends(get_async_session)
) -> TokenDataSchema:
    payload = decode_jwt(token.refresh_token.encode())
    user_token = await get_current_auth_user_for_refresh(token.refresh_token, db)
    tokens = await create_tokens(user_token, db, payload['device_id'])
    await revoke_refresh_token(token.refresh_token, db, payload['device_id'])
    return tokens


@router.post("/sign-up")
async def signup(user: UsersAddSchema,
                 db: AsyncSession = Depends(get_async_session),
                 ) -> TokenDataSchema:
    data_user = await create_user(user, db)
    tokens = await create_tokens(data_user, db)
    return tokens
