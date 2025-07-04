from datetime import timedelta

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from src.auth.validation import (
    validate_token_type,
    verify_refresh_token
)
from src.config.settings import settings
from src.auth.schemas import UsersSchema
from src.auth.services import (
    create_jwt,
    decode_jwt,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)
from src.auth.crud import get_user

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/sign-in/",
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
    token: str = Depends(oauth2_scheme),
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
        db: AsyncSession,
        payload: dict = Depends(get_current_token_payload),
        token_type: str = ACCESS_TOKEN_TYPE
) -> UsersSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid",
    )
    validate_token_type(payload, token_type)
    username: str | None = payload.get("sub")
    if not verify_refresh_token(payload, username, db):
        raise unauthed_exc
    user = await get_user(username, db)
    if user:
        return user
    raise unauthed_exc


def get_current_active_auth_user(
    db: AsyncSession,
) -> UsersSchema:
    user: UsersSchema = await get_user_by_token_sub(db=db, token_type=REFRESH_TOKEN_TYPE)
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="inactive user",
    )
