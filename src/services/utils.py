import logging
import uuid
from datetime import timedelta

from services.security import create_jwt, decode_jwt
from src.core.settings import settings
from src.schemas.user import UsersSchema


logger = logging.getLogger(__name__)


def create_access_token(user: UsersSchema, jti: str, device_id: str) -> str:
    jwt_payload = {
        "jti": jti,
        "sub": user.username,
        "username": user.username,
        "email": user.email,
        "device_id": device_id
    }
    return create_jwt(
        token_type=settings.jwt_settings.ACCESS_TOKEN_TYPE,
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
        token_type=settings.jwt_settings.REFRESH_TOKEN_TYPE,
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


def get_payload_with_header(authorization) -> dict:
    token = authorization.replace('Bearer ', '')
    payload = decode_jwt(token.encode())
    return payload
