from datetime import timedelta, datetime

import jwt
import uuid
from faker import Faker
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.security import get_hash_password, decode_jwt
from src.database.models.user import UsersOrm, TokenOrm
from src.schemas.user import UsersSchema
from src.core.settings import settings
from src.services.validations import validate_password

faker = Faker()


def get_user_data(
        username_or_email: str,
        user_credentials_data: dict) -> dict:
    if username_or_email == "username":
        username = user_credentials_data.get("username")
    else:
        username = user_credentials_data.get("email")
    return {
        "username": username,
        "password": user_credentials_data.get("password")
    }


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
        user: UsersSchema,
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
    token = TokenOrm(
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


async def update_refresh_token(
        refresh_token: str,
        expired: bool,
        revoked: bool,
        session: AsyncSession,
) -> None:
    now = datetime.utcnow()
    expire_delta = timedelta(days=-1) if expired else timedelta(days=30)
    expires_at = now + expire_delta
    async with session:
        await session.execute(
            update(TokenOrm)
            .where(TokenOrm.token == refresh_token)
            .values(
                expires_at=expires_at,
                revoked=revoked
            )
        )
        await session.commit()


def create_test_access_token(
        user: UsersSchema,
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


async def verify_user_db(
        user_credentials_data: dict,
        session: AsyncSession
) -> bool:
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


async def get_refresh_token(
        token: str,
        session: AsyncSession
) -> TokenOrm:
    async with session:
        query = select(TokenOrm).options(
            joinedload(TokenOrm.user)
        ).filter(
            TokenOrm.token == token
        )
        result = await session.execute(query)
        token_db = result.unique().scalars().first()
    return token_db


async def verify_refresh_token(
        token: str,
        username: str,
        session: AsyncSession
) -> None:
    token = await get_refresh_token(token, session)
    username_db = token.user.username
    assert token is not None
    assert username_db == username


async def verify_refresh_token_revoke(
        token: str,
        session: AsyncSession
) -> bool:
    token = await get_refresh_token(token, session)
    if token.revoked:
        return True
    return False


async def get_user(
        user_email: str,
        session: AsyncSession
) -> UsersSchema:
    async with session:
        user = await session.execute(
            select(UsersOrm)
            .where(UsersOrm.email == user_email)
        )
    return user.scalars().first()


async def verify_change_password(
        user_email: str,
        new_password: str,
        session: AsyncSession
) -> bool:
    user = await get_user(user_email, session)
    return validate_password(new_password, user.password)


async def check_confirm_user(
        user_email: str,
        session: AsyncSession
) -> bool:
    user = await get_user(user_email, session)
    return user.is_verified
