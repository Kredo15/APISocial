from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import InvalidTokenError

from src.auth.validation import (
    verify_refresh_token
)
from src.config.settings import settings
from src.auth.schemas import UsersSchema, TokenDataSchema
from src.auth.services import (
    create_jwt,
    decode_jwt,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)
from src.auth.crud import get_user, add_refresh_token


async def create_tokens(user: UsersSchema,
                        db: AsyncSession
                        ) -> TokenDataSchema:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    await add_refresh_token(refresh_token, user.username, db)
    return TokenDataSchema(
            access_token=access_token,
            refresh_token=refresh_token
    )


def create_access_token(user: UsersSchema) -> str:
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token(user: UsersSchema) -> str:
    jwt_payload = {
        "sub": user.username
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def get_current_token_payload(
    token: str,
) -> dict:
    try:
        payload = decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
        )
    return payload


async def get_user_by_token_sub(
        token: str,
        db: AsyncSession
) -> dict:
    payload = get_current_token_payload(token)
    username: str = payload.get("sub")
    valid_token = await verify_refresh_token(token, username, db)
    if not valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token invalid",
        )
    return payload


def get_current_auth_user_for_refresh(
    token: str,
    db: AsyncSession,
) -> UsersSchema:
    payload = await get_user_by_token_sub(token, db)
    username: str = payload.get("sub")
    user = await get_user(username, db)
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="inactive user",
    )
