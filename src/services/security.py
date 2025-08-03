from datetime import datetime, timedelta
import uuid
import logging

import bcrypt
from itsdangerous import URLSafeTimedSerializer
import jwt
from fastapi import status, HTTPException

from src.message import LogMessages
from src.core.settings import settings

logger = logging.getLogger(__name__)


def get_hash_password(
    password: str,
) -> str:
    pwhash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return pwhash.decode('utf-8')


def generate_token(to_email: str) -> str:
    serializer = URLSafeTimedSerializer(settings.email_settings.SECRET_KEY_EMAIL.get_secret_value())
    return serializer.dumps(to_email, salt=settings.email_settings.SECURITY_PASSWORD_SALT.get_secret_value())


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
    jwt_payload = {settings.jwt_settings.TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )
