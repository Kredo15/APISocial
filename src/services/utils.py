import logging
import uuid
from datetime import datetime, timedelta

import jwt
from fastapi import status, HTTPException

from src.message import LogMessages
from src.core.settings import settings
from src.schemas.user import UsersSchema


logger = logging.getLogger(__name__)

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


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
        expire_minutes=settings.jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
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
        expire_timedelta=timedelta(days=settings.jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def get_current_token_payload(
        token: str,
) -> dict:
    payload = decode_jwt(
        token=token.encode(),
    )
    return payload


def get_jti_or_device_id() -> str:
    return str(uuid.uuid4())


def encode_jwt(
    payload: dict,
    private_key: str = settings.jwt_settings.PRIVATE_KEY_PATH.read_text(),
    algorithm: str = settings.jwt_settings.ALGORITHM,
    expire_minutes: int = settings.jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4())
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: bytes,
    public_key: str = settings.jwt_settings.PUBLIC_KEY_PATH.read_text(),
    algorithm: str = settings.jwt_settings.ALGORITHM,
) -> dict:
    try:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=[algorithm],
        )
        return decoded
    except jwt.InvalidTokenError:
        logger.error(LogMessages.JWT_DECODE_INVALID)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error",
        )


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def get_payload_with_header(authorization) -> dict:
    token = authorization.replace('Bearer ', '')
    payload = decode_jwt(token.encode())
    return payload
