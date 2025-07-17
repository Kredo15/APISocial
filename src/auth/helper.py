from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import decode_jwt, get_token_with_header
from src.auth.validation import validate_auth_user, verify_user
from src.auth.utils import (
    create_tokens,
    get_current_auth_user_for_refresh,
)
from src.auth.crud import create_user, revoke_refresh_token, revoke_all_refresh_token_for_device
from src.auth.schemas import (
    TokenDataSchema,
    UsersAddSchema,
    UpdateTokensIn
)


async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm,
    db: AsyncSession
) -> TokenDataSchema:
    data_user = await validate_auth_user(form_data, db)
    tokens = await create_tokens(data_user, db)
    return tokens


async def auth_refresh_jwt(
    token: UpdateTokensIn,
    db: AsyncSession
) -> TokenDataSchema:
    payload = decode_jwt(token.refresh_token.encode())

    user_token = await get_current_auth_user_for_refresh(token.refresh_token, db)
    await revoke_refresh_token(payload, db)
    tokens = await create_tokens(user_token, db, payload['device_id'])
    return tokens


async def register_user(
    user: UsersAddSchema,
    db: AsyncSession
) -> TokenDataSchema:
    await verify_user(user, db)
    data_user = await create_user(user, db)
    tokens = await create_tokens(data_user, db)
    return tokens


async def logout_user(
    request: Request,
    db: AsyncSession
) -> None:
    token = get_token_with_header(request.headers['authorization'])
    payload = decode_jwt(token.encode())
    await revoke_all_refresh_token_for_device(payload, db)
