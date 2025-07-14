from datetime import timedelta, datetime

import jwt
import uuid
from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.auth.models import TokenOrm, UsersOrm
from src.auth.schemas import UsersSchema
from src.auth.services import decode_jwt, get_hash_password

faker = Faker()


def get_user_data(login_username_or_email, user_credentials_data) -> dict:
    if login_username_or_email == "username":
        username = user_credentials_data.get("username")
    else:
        username = user_credentials_data.get("email")
    return {
        "username": username,
        "password": user_credentials_data.get("password")
    }


async def create_test_user(user_data: dict,
                           async_session: AsyncSession):
    user = UsersOrm(
        username=user_data['username'],
        email=user_data['email'],
        password=get_hash_password(user_data['password']),
    )
    async with async_session:
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
    return user


async def create_test_refresh_token(
        user: UsersSchema,
        device_id: str,
        session: AsyncSession,
        private_key: str = settings.PRIVATE_KEY_PATH.read_text(),
        algorithm: str = settings.ALGORITHM,
        expired: bool = False,
        revoked: bool = False,
) -> str:
    now = datetime.utcnow()
    expire_delta = timedelta(days=-1) if expired else timedelta(days=30)
    expires_at = now + expire_delta

    jwt_payload = {
        "type": "refresh",
        "sub": user.username,
        'exp': expires_at,
        'iat': now,
        'jti': str(uuid.uuid4()),
        'device_id': device_id
    }
    refresh_token = jwt.encode(jwt_payload, private_key, algorithm=algorithm)
    token = TokenOrm(
        token=refresh_token,
        user=user,
        device_id=device_id,
        expires_at=expires_at,
        revoked=revoked
    )
    async with session:
        session.add(token)
        await session.commit()

    return refresh_token


def create_test_access_token(
        user: UsersSchema,
        device_id: str,
        private_key: str = settings.PRIVATE_KEY_PATH.read_text(),
        algorithm: str = settings.ALGORITHM,
        expired: bool = False,
) -> str:
    now = datetime.utcnow()
    expire_delta = timedelta(minutes=-1) if expired else timedelta(minutes=30)
    expires_at = now + expire_delta
    jwt_payload = {
        "type": "access",
        "sub": user.username,
        "username": user.username,
        "email": user.email,
        'exp': expires_at,
        'iat': now,
        'jti': str(uuid.uuid4()),
        'device_id': device_id
    }
    access_token = jwt.encode(jwt_payload, private_key, algorithm=algorithm)
    return access_token


async def verify_user_db(user_credentials_data: dict,
                         session: AsyncSession) -> bool:
    async with session:
        user = await session.execute(select(UsersOrm).filter(
            UsersOrm.email == user_credentials_data.get('email'),
            UsersOrm.username == user_credentials_data.get('username')
        ))
    return user is not None


def verify_access_token(token: str, user_credentials_data: dict) -> None:
    payload = decode_jwt(
        token=token.encode(),
    )
    assert payload.get('sub') == user_credentials_data.get('username')
    assert payload.get('username') == user_credentials_data.get('username')
    assert payload.get('email') == user_credentials_data.get('email')


async def verify_refresh_token(
        token: str,
        username: str,
        session: AsyncSession
) -> None:
    async with session:
        query = select(TokenOrm).options(
            joinedload(TokenOrm.user)
        ).filter(
            TokenOrm.token == token
        )
        result = await session.execute(query)
        token_db = result.unique().scalars().first()
        username_db = token_db.user.username
    assert token_db is not None
    assert username_db == username
