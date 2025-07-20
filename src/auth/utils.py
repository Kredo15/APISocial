import logging
from datetime import timedelta


from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.validation import (
    verify_refresh_token,
    validate_token_type
)
from src.common.message import LogMessages
from src.config.settings import settings
from src.auth.schemas import UsersSchema, TokenDataSchema
from src.auth.services import (
    create_jwt,
    decode_jwt,
    get_jti_or_device_id,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)
from src.auth.crud import (
    get_user,
    add_refresh_token,
    update_last_login
)

logger = logging.getLogger(__name__)


async def create_tokens(
        user: UsersSchema,
        db: AsyncSession,
        jti: str = get_jti_or_device_id(),
        device_id: str = get_jti_or_device_id()
) -> TokenDataSchema:
    access_token = create_access_token(user, jti, device_id)
    refresh_token = create_refresh_token(user, jti, device_id)
    await add_refresh_token(jti, refresh_token, user, device_id, db)
    await update_last_login(user, db)
    return TokenDataSchema(
        access_token=access_token,
        refresh_token=refresh_token
    )


def create_access_token(user: UsersSchema, jti: str, device_id: str) -> str:
    jwt_payload = {
        "jti": jti,
        "sub": user.username,
        "username": user.username,
        "email": user.email,
        "device_id": device_id
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token(user: UsersSchema, jti: str, device_id: str) -> str:
    jwt_payload = {
        "jti": jti,
        "sub": user.username,
        "device_id": device_id
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def get_current_token_payload(
        token: str,
) -> dict:
    payload = decode_jwt(
        token=token.encode(),
    )
    return payload


async def get_user_by_token_sub(
        token: str,
        token_type: str,
        db: AsyncSession
) -> UsersSchema:
    payload = get_current_token_payload(token)
    validate_token_type(payload, token_type)
    username: str = payload.get("sub")
    user = await get_user(username, db)
    if not user.is_active:
        logger.error(LogMessages.USER_INACTIVE.format(user_id=user.uid))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="inactive user",
        )
    return user


async def get_current_auth_user_for_refresh(
        token: str,
        db: AsyncSession
) -> UsersSchema:
    user = await get_user_by_token_sub(token, REFRESH_TOKEN_TYPE, db)
    valid_token = await verify_refresh_token(token, user, db)
    if not valid_token:
        logger.error(LogMessages.JWT_INACTIVE.format(user_id=user.uid))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error",
        )
    return user
