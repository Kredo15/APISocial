from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

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
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: UsersSchema) -> str:
    jwt_payload = {
        "sub": user.username
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
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


def get_user_by_token_sub(payload: dict) -> UsersSchema:
    username: str | None = payload.get("sub")
    if user := await get_user(username):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid (user not found)",
    )
