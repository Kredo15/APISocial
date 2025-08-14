from datetime import timedelta, datetime

import jwt
import uuid
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.security import get_hash_password
from src.database.models.user import UsersOrm, TokensOrm
from src.schemas.user_schema import UserSchema
from src.core.settings import settings

faker = Faker()


async def create_test_user(
        user_data: dict,
        async_session: AsyncSession,
        is_active: bool = True
):
    user = UsersOrm(
        username=user_data['username'],
        email=user_data['email'],
        password=get_hash_password(user_data['password']),
        is_active=is_active
    )
    async with async_session:
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
    return user


async def create_test_refresh_token(
        user: UserSchema,
        data_for_token: dict,
        session: AsyncSession,
        private_key: str = settings.jwt_settings.PRIVATE_KEY_PATH.read_text(),
        algorithm: str = settings.jwt_settings.ALGORITHM,
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
        'jti': data_for_token['jti'],
        'device_id': data_for_token['device_id']
    }
    refresh_token = jwt.encode(jwt_payload, private_key, algorithm=algorithm)
    token = TokensOrm(
        jti=data_for_token['jti'],
        token=refresh_token,
        user=user,
        device_id=data_for_token['device_id'],
        expires_at=expires_at,
        revoked=revoked
    )
    async with session:
        session.add(token)
        await session.commit()

    return refresh_token


def create_test_access_token(
        user: UserSchema,
        device_id: str,
        private_key: str = settings.jwt_settings.PRIVATE_KEY_PATH.read_text(),
        algorithm: str = settings.jwt_settings.ALGORITHM,
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


async def get_user(
        user_email: str,
        async_session: AsyncSession
) -> UserSchema:
    async with async_session:
        user = await async_session.execute(
            select(UsersOrm)
            .where(UsersOrm.email == user_email)
        )
    return user.scalars().first()
