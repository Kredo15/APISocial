from datetime import timedelta, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.security import decode_jwt
from src.database.models.user import UsersOrm, TokensOrm
from tests.for_test import get_user


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
            update(TokensOrm)
            .where(TokensOrm.token == refresh_token)
            .values(
                expires_at=expires_at,
                revoked=revoked
            )
        )
        await session.commit()


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
) -> TokensOrm:
    async with session:
        query = select(TokensOrm).options(
            joinedload(TokensOrm.user)
        ).filter(
            TokensOrm.token == token
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


async def check_confirm_user(
        user_email: str,
        session: AsyncSession
) -> bool:
    user = await get_user(user_email, session)
    return user.is_verified
