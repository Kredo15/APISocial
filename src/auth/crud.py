from datetime import datetime, timedelta
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select, insert
from pydantic import EmailStr

from src.database.db import get_async_session
from src.auth.schemas import UsersAddSchema, UsersSchema, TokenSchema
from src.auth.models import UsersOrm, TokenOrm
from src.auth.services import get_hash_password
from src.config.settings import settings


async def get_user(
        username: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> UsersSchema:
    user = await db.scalar(select(UsersOrm).where(UsersOrm.username == username))
    return user


async def get_user_for_email(
        email: EmailStr,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> UsersSchema:
    user = await db.scalar(select(UsersOrm).where(UsersOrm.email == email))
    return user


async def create_user(
        user_data: UsersAddSchema,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> UsersSchema:
    hashed_password = get_hash_password(user_data.password)
    data = {
        "email": user_data.email,
        "username": user_data.username,
        "password": hashed_password
    }
    user = await db.scalar(insert(UsersOrm).returning(UsersOrm), data)
    return user


async def update_last_login(
        user: UsersSchema,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    now = datetime.utcnow()
    async with db:
        user.last_login = now
        await db.commit()


async def add_refresh_token(
        jti: str,
        refresh_token: str,
        user: UsersSchema,
        device_id: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    now = datetime.utcnow()
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token = TokenOrm(
        jti=jti,
        token=refresh_token,
        user=user,
        device_id=device_id,
        expires_at=expire
    )
    async with db:
        db.add(token)
        await db.commit()


async def get_token(
        token: str, user: UsersSchema,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> TokenSchema:
    token_db = await db.scalar(select(TokenOrm).where(
        TokenOrm.user == user,
        TokenOrm.token == token,
        TokenOrm.expires_at >= datetime.utcnow(),
        TokenOrm.revoked == False)
    )
    return token_db


async def revoke_refresh_token(
        payload: dict,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    db_token = await db.execute(select(TokenOrm).filter(
        TokenOrm.jti == payload['jti'],
        TokenOrm.device_id == payload['device_id']
    ))
    if db_token:
        db_token.revoked = True
        await db.commit()


async def revoke_all_refresh_token_for_device(
        payload: dict,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    db_tokens = await db.scalars(select(TokenOrm).filter(
        TokenOrm.device_id == payload['device_id'],
        TokenOrm.revoked == False
    ))
    for token in db_tokens:
        token.revoked = True
    await db.commit()
